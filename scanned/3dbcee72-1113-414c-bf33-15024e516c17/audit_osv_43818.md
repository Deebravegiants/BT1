# [C] openssl_encrypt before 1.4.0 HMAC Authentication Bypass via Environment Variable

## Summary
Severity: Critical
Advisory: CVE-2026-74890
Aliases: GHSA-rvc2-5jxq-gpcj, PYSEC-2026-3766
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-74890
Type: osv

## Details
openssl_encrypt versions before 1.4.0 contain an authentication bypass vulnerability in CamelliaCipher that disables HMAC tag generation and verification when the PYTEST_CURRENT_TEST environment variable is set. Attackers with code execution can set this environment variable to produce unauthenticated ciphertext and bypass integrity protection on encrypted data.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74890.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-rvc2-5jxq-gpcj
- https://nvd.nist.gov/vuln/detail/CVE-2026-74890
- https://www.vulncheck.com/advisories/openssl-encrypt-before-hmac-authentication-bypass-via-environment-variable
