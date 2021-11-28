"""buttons definition"""

import json
def text_button(label, color, payload=""):
    """definition of a buttin with text"""
    return {
        "action": {
            "type": "text",
            "payload": json.dumps(payload),
            "label": label
        },
        "color": color
    }


def location_button(payload=""):
    """definition of a button with location"""
    return {
        "action": {
            "type": "location",
            "payload": json.dumps(payload)
        }
    }
