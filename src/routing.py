"""
Alexis Bot
"""

# Structure: BANK_NAME -> STATE_CODE -> routing_number
# If a bank uses one national routing, state maps to the same number.
ROUTING_TABLE: dict[str, dict[str, str]] = {
    "bank of america": {
        "ca": "121000358",
        "tx": "111000025",
        "fl": "063100277",
        "ny": "021000322",
        "il": "081904808",
        "az": "122101706",
        "nv": "122101706",
        "default": "026009593",  # East Coast / general
    },
    "wells fargo": {
        "ca": "121042882",
        "tx": "111900659",
        "fl": "063107513",
        "ny": "026012881",
        "il": "071101307",
        "az": "122105155",
        "default": "121042882",
    },
    "chase": {
        "ca": "322271627",
        "tx": "111000614",
        "fl": "267084131",
        "ny": "021000021",
        "il": "071000013",
        "az": "122100024",
        "default": "021000021",
    },
    "citibank": {
        "ca": "322271724",
        "tx": "113193532",
        "fl": "266086554",
        "ny": "021000089",
        "il": "271070801",
        "default": "021000089",
    },
    "td bank": {
        "ny": "026013673",
        "fl": "067014822",
        "nj": "031201360",
        "ma": "211274450",
        "default": "026013673",
    },
    "regions bank": {
        "fl": "063104668",
        "tx": "062000019",
        "al": "062000019",
        "tn": "064000017",
        "default": "062000019",
    },
    "bbva usa": {
        # BBVA USA was acquired by PNC in 2021; routing numbers vary by legacy region
        "tx": "113010547",
        "al": "062001186",
        "az": "122105045",
        "ca": "122105045",
        "default": "062001186",
    },
    "popular bank": {
        # Banco Popular — highly used by Puerto Rican/Latino community
        "ny": "021571415",
        "fl": "067010867",
        "nj": "021571415",
        "default": "021571415",
    },
    "banregio": {
        # Banregio (Mexican bank with US presence via wire partnerships)
        # No direct ACH in US; included for reference — agent should flag this
        "default": "N/A - no ACH directo en EE.UU.",
    },
    "chase (latino)": {
        # Alias used when customer says "Chase" in Spanish-speaking context
        "ca": "322271627",
        "tx": "111000614",
        "fl": "267084131",
        "ny": "021000021",
        "default": "021000021",
    },
    "us bank": {
        "ca": "122235821",
        "tx": "091000022",
        "il": "071904779",
        "mn": "091000022",
        "default": "091000022",
    },
}

# State normalization map
STATE_ALIASES: dict[str, str] = {
    "california": "ca",
    "texas": "tx",
    "florida": "fl",
    "new york": "ny",
    "illinois": "il",
    "arizona": "az",
    "nevada": "nv",
    "new jersey": "nj",
    "massachusetts": "ma",
    "alabama": "al",
    "tennessee": "tn",
    "minnesota": "mn",
    # abbreviations already normalized
    "ca": "ca",
    "tx": "tx",
    "fl": "fl",
    "ny": "ny",
    "il": "il",
    "az": "az",
    "nv": "nv",
    "nj": "nj",
    "ma": "ma",
    "al": "al",
    "tn": "tn",
    "mn": "mn",
}

# Bank name normalization
BANK_ALIASES: dict[str, str] = {
    "boa": "bank of america",
    "bofa": "bank of america",
    "bank of america": "bank of america",
    "banco de america": "bank of america",
    "wells": "wells fargo",
    "wells fargo": "wells fargo",
    "chase": "chase",
    "jpmorgan": "chase",
    "jp morgan": "chase",
    "citi": "citibank",
    "citibank": "citibank",
    "citibanks": "citibank",
    "td": "td bank",
    "td bank": "td bank",
    "regions": "regions bank",
    "regions bank": "regions bank",
    "bbva": "bbva usa",
    "bbva usa": "bbva usa",
    "popular": "popular bank",
    "banco popular": "popular bank",
    "banpopular": "popular bank",
    "banregio": "banregio",
    "us bank": "us bank",
    "usbank": "us bank",
    "u.s. bank": "us bank",
}


def normalize_bank(bank_input: str) -> str | None:
    """Return canonical bank key or None if not recognized."""
    key = bank_input.lower().strip()
    return BANK_ALIASES.get(key)


def normalize_state(state_input: str) -> str | None:
    """Return 2-letter state code or None if not recognized."""
    key = state_input.lower().strip()
    return STATE_ALIASES.get(key)


def lookup_routing(bank_input: str, state_input: str) -> dict:
    """
    Returns a dict with:
      - routing: str (number or N/A)
      - bank: str (canonical name)
      - state: str (2-letter code)
      - found: bool
      - message: str (human-readable explanation)
    """
    bank = normalize_bank(bank_input)
    state = normalize_state(state_input)

    if not bank:
        return {
            "found": False,
            "routing": None,
            "bank": bank_input,
            "state": state_input,
            "message": (
                f"No encontré el banco '{bank_input}' en mi base de datos. "
                "Por favor verifica el nombre exacto o consulta el routing directamente "
                "en tu estado de cuenta o sitio web del banco."
            ),
        }

    bank_routes = ROUTING_TABLE.get(bank, {})

    if state and state in bank_routes:
        routing = bank_routes[state]
    else:
        routing = bank_routes.get("default", "No disponible")

    if routing == "N/A - no ACH directo en EE.UU.":
        return {
            "found": False,
            "routing": None,
            "bank": bank,
            "state": state or state_input,
            "message": (
                f"{bank.title()} no tiene routing ACH directo en EE.UU. "
                "Te recomendamos usar Wire Transfer o contactar a tu banco."
            ),
        }

    state_label = state.upper() if state else state_input.upper()
    return {
        "found": True,
        "routing": routing,
        "bank": bank.title(),
        "state": state_label,
        "message": (
            f"El routing number de {bank.title()} en {state_label} es: *{routing}*\n"
            "_Nota: Verifica siempre en tu estado de cuenta o la app de tu banco._"
        ),
    }
