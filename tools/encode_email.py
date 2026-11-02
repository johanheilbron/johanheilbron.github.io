#!/usr/bin/env python3
"""
encode_email.py: encode an e-mail address for content/site.yaml (email_encoded).

The address is reversed and then base64-encoded, so it appears in plain text
neither in the public repository nor in the published HTML. assets/site.js
decodes it when a visitor clicks "Show e-mail address".

Usage:
    uv run tools/encode_email.py name@example.org
"""

import base64
import sys

if len(sys.argv) != 2:
    sys.exit(__doc__)
print(base64.b64encode(sys.argv[1][::-1].encode("utf-8")).decode("ascii"))
