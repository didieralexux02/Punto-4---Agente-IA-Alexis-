"""
NACHA Return Codes — ACH Failure Handling
Covers the most common rejection reasons for ACH pull transactions.
"""

NACHA_CODES: dict[str, dict] = {
    "R01": {
        "name": "Insufficient Funds",
        "description": "La cuenta de origen no tiene fondos suficientes para cubrir el débito.",
        "client_message": (
            "⚠️ *Tu transferencia fue rechazada (R01 – Fondos insuficientes).*\n\n"
            "Tu cuenta bancaria no tenía el saldo necesario al momento del débito. "
            "Por favor verifica tu saldo y vuelve a intentarlo cuando tengas fondos disponibles.\n\n"
            "💡 *¿Qué puedes hacer?*\n"
            "1. Asegúrate de tener el monto + cualquier cargo del banco disponible.\n"
            "2. Inicia una nueva transferencia desde la app de Insights.\n"
            "3. Considera usar Same-Day ACH para fondos urgentes.\n\n"
            "Si el problema persiste, contacta a soporte: support@insights.com"
        ),
        "escalate": False,
        "retry_allowed": True,
    },
    "R02": {
        "name": "Account Closed",
        "description": "La cuenta bancaria fue cerrada por el titular.",
        "client_message": (
            "🚫 *Tu transferencia fue rechazada (R02 – Cuenta cerrada).*\n\n"
            "La cuenta bancaria que registraste ya no está activa. "
            "Necesitas actualizar tu información bancaria.\n\n"
            "💡 *Pasos a seguir:*\n"
            "1. Ve a Configuración → Métodos de pago en la app de Insights.\n"
            "2. Elimina la cuenta bancaria anterior.\n"
            "3. Agrega tu nueva cuenta bancaria.\n\n"
            "Si necesitas ayuda, estamos en support@insights.com"
        ),
        "escalate": True,
        "retry_allowed": False,
    },
    "R03": {
        "name": "No Account / Unable to Locate Account",
        "description": "El número de cuenta o el routing number no corresponden a ninguna cuenta válida.",
        "client_message": (
            "🚫 *Tu transferencia fue rechazada (R03 – Cuenta no encontrada).*\n\n"
            "Los datos bancarios que proporcionaste (routing o número de cuenta) "
            "no coinciden con ninguna cuenta activa en ese banco.\n\n"
            "💡 *Por favor verifica:*\n"
            "1. ✅ Routing number correcto para tu banco Y estado.\n"
            "2. ✅ Número de cuenta (no el número de tarjeta).\n"
            "3. ✅ Que la cuenta sea de cheques (checking), no ahorros.\n\n"
            "Vuelve a ingresar los datos desde la app. "
            "Ante dudas, consulta tu estado de cuenta físico o la app de tu banco."
        ),
        "escalate": True,
        "retry_allowed": True,
    },
    "R04": {
        "name": "Invalid Account Number",
        "description": "El número de cuenta tiene un formato inválido.",
        "client_message": (
            "⚠️ *Tu transferencia fue rechazada (R04 – Número de cuenta inválido).*\n\n"
            "El número de cuenta que ingresaste no tiene el formato correcto. "
            "Los números de cuenta bancaria en EE.UU. tienen entre 4 y 17 dígitos.\n\n"
            "Verifica el número en tu chequera o app bancaria e intenta de nuevo."
        ),
        "escalate": False,
        "retry_allowed": True,
    },
    "R07": {
        "name": "Authorization Revoked",
        "description": "El cliente revocó el permiso de débito ACH.",
        "client_message": (
            "🔒 *Tu transferencia fue detenida (R07 – Autorización revocada).*\n\n"
            "Tu banco registra que revocaste el permiso para débitos automáticos. "
            "Para reanudar el fondeo ACH deberás autorizar nuevamente desde la app de Insights."
        ),
        "escalate": True,
        "retry_allowed": False,
    },
    "R10": {
        "name": "Customer Advises Not Authorized",
        "description": "El cliente reportó a su banco que no autorizó el cargo.",
        "client_message": (
            "🔒 *Tu transferencia fue detenida (R10 – No autorizada).*\n\n"
            "Tu banco recibió una disputa indicando que no autorizaste este débito. "
            "Si fue un error, contacta a soporte de Insights de inmediato: support@insights.com"
        ),
        "escalate": True,
        "retry_allowed": False,
    },
}


def get_failure_response(code: str) -> dict:
    """Return the failure info for a given NACHA code."""
    code = code.upper().strip()
    if code in NACHA_CODES:
        return NACHA_CODES[code]
    return {
        "name": "Unknown Error",
        "description": f"Código no reconocido: {code}",
        "client_message": (
            f"⚠️ Tu transferencia fue rechazada con el código *{code}*.\n\n"
            "Nuestro equipo de soporte revisará el caso. "
            "Contacta a support@insights.com para asistencia inmediata."
        ),
        "escalate": True,
        "retry_allowed": False,
    }
