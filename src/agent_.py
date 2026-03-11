"""
Alexis Agent 
"""
import os
import re
import anthropic
from system_prompt import get_system_prompt
from routing import lookup_routing, normalize_bank, normalize_state
from nacha_codes import get_failure_response

ANTHROPIC_MODEL = "claude-sonnet-4-20250514"

# Regex patterns for detecting NACHA codes in user messages
NACHA_PATTERN = re.compile(r'\b(R0[1-9]|R1[0-9]|R2[0-9]|R3[0-9])\b', re.IGNORECASE)


class ACHAgent:
    """
    Stateful ACH funding assistant.
    Maintains conversation history and injects routing context dynamically.
    """

    def __init__(self):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.history: list[dict] = []
        self.collected_bank: str | None = None
        self.collected_state: str | None = None
        self.routing_injected: bool = False

    def get_welcome_message(self) -> str:
        return (
            "👋 *¡Bienvenido a Insights!*\n\n"
            "Soy tu asistente para fondear tu cuenta de inversión mediante transferencia bancaria (ACH).\n\n"
            "¿Deseas fondear tu cuenta hoy? Cuéntame cómo puedo ayudarte 🚀"
        )

    def _extract_bank_and_state(self, text: str):
        """
        Try to extract bank name and state from the user's message.
        Runs simple heuristic before sending to the LLM.
        """
        text_lower = text.lower()

        # Common patterns: "chase en texas", "bank of america in california"
        patterns = [
            r'(bank of america|boa|bofa|wells fargo|wells|chase|citi|citibank|td bank|td|'
            r'regions|bbva|popular|banco popular|us bank|banregio)'
            r'(?:\s+(?:en|in)\s+)'
            r'(california|texas|florida|new york|illinois|arizona|nevada|'
            r'new jersey|massachusetts|alabama|tennessee|minnesota|'
            r'ca|tx|fl|ny|il|az|nv|nj|ma|al|tn|mn)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                bank_raw = match.group(1)
                state_raw = match.group(2)
                bank = normalize_bank(bank_raw)
                state = normalize_state(state_raw)
                if bank:
                    self.collected_bank = bank_raw
                if state:
                    self.collected_state = state_raw

    def _build_routing_context(self) -> str | None:
        """
        If we have both bank and state, compute routing and return a context string
        to inject as a system note into the conversation.
        """
        if self.collected_bank and self.collected_state and not self.routing_injected:
            result = lookup_routing(self.collected_bank, self.collected_state)
            self.routing_injected = True
            if result["found"]:
                return (
                    f"[CONTEXTO INTERNO — NO MOSTRAR AL CLIENTE LITERALMENTE] "
                    f"Routing inferido para {result['bank']} en {result['state']}: "
                    f"{result['routing']}. Comunícalo al cliente claramente."
                )
            else:
                return (
                    f"[CONTEXTO INTERNO] No se encontró routing para "
                    f"'{self.collected_bank}' en '{self.collected_state}'. "
                    f"Indica al cliente cómo encontrarlo por su cuenta."
                )
        return None

    def _check_nacha_code(self, text: str) -> str | None:
        """If user mentions a NACHA code, return the structured failure response."""
        match = NACHA_PATTERN.search(text)
        if match:
            code = match.group(1).upper()
            failure = get_failure_response(code)
            return failure["client_message"]
        return None

    def process_message(self, user_input: str) -> str:
        # 1. Check for NACHA failure codes first (direct override)
        nacha_response = self._check_nacha_code(user_input)
        if nacha_response:
            self.history.append({"role": "user", "content": user_input})
            self.history.append({"role": "assistant", "content": nacha_response})
            return nacha_response

        # 2. Try to extract bank/state from user message
        self._extract_bank_and_state(user_input)

        # 3. Build messages list
        messages = list(self.history)
        messages.append({"role": "user", "content": user_input})

        # 4. Inject routing context if available
        routing_context = self._build_routing_context()
        if routing_context:
            # Inject as an extra user message before the actual question
            # so the model has the data available this turn
            messages_with_ctx = list(self.history)
            messages_with_ctx.append({
                "role": "user",
                "content": f"{user_input}\n\n{routing_context}"
            })
        else:
            messages_with_ctx = messages

        # 5. Call Anthropic API
        response = self.client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=1024,
            system=get_system_prompt(),
            messages=messages_with_ctx,
        )

        assistant_text = response.content[0].text

        # 6. Update history with clean versions (no internal context)
        self.history.append({"role": "user", "content": user_input})
        self.history.append({"role": "assistant", "content": assistant_text})

        return assistant_text
