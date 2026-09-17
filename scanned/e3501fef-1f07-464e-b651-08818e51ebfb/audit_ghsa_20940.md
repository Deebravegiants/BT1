# [C] python-jwt vulnerable to token forgery with new claims

## Summary
Severity: Critical
Advisory: GHSA-5p8v-58qm-c7fp
CVE: CVE-2022-39227
CWE: CWE-290
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-09-21
Source: https://github.com/advisories/GHSA-5p8v-58qm-c7fp
Type: github-advisory

## Affected
- PyPI: `python-jwt` — affected >=0 <3.3.4

## Details
### Impact
An attacker who obtains a JWT can arbitrarily forge its contents without knowing the secret key. Depending on the application, this may for example enable the attacker to spoof other user's identities, hijack their sessions, or bypass authentication.

### Patches
Users should upgrade to version 3.3.4
Fixed by: https://github.com/davedoesdev/python-jwt/commit/88ad9e67c53aa5f7c43ec4aa52ed34b7930068c9

### Workarounds
None

### References
Found by [Tom Tervoort](Tom.Tervoort@secura.com)
https://github.com/pypa/advisory-database/blob/main/vulns/python-jwt/PYSEC-2022-259.yaml

### More information

The vulnerability allows an attacker, who possesses a single valid JWT, to create a new token with forged claims that the verify_jwt function will accept as valid.

The issue is caused by an inconsistency between the JWT parsers used by python-jwt and its dependency jwcrypto. By mixing compact and JSON representations, an attacker can trick jwcrypto of parsing different claims than those over which a signature is validated by jwcrypto.

Testing the fix has been added as an [automated unit test](https://github.com/davedoesdev/python-jwt/blob/master/test/vulnerability_vows.py) to python-jwt.

If you have any questions or comments about this advisory, please open an issue in [python-jwt](https://github.com/davedoesdev/python-jwt)

## References
- https://github.com/davedoesdev/python-jwt/security/advisories/GHSA-5p8v-58qm-c7fp
- https://nvd.nist.gov/vuln/detail/CVE-2022-39227
- https://github.com/davedoesdev/python-jwt/commit/6c5075469847b9e8b6e5336077d989d77a4d2bf1
- https://github.com/davedoesdev/python-jwt/commit/88ad9e67c53aa5f7c43ec4aa52ed34b7930068c9
- https://github.com/davedoesdev/python-jwt
- https://github.com/pypa/advisory-database/blob/main/vulns/python-jwt/PYSEC-2022-259.yaml
- https://www.vicarius.io/vsociety/posts/authentication-bypass-in-python-jwt
