# [C] openssl_encrypt before 1.4.0 Authentication Bypass via Bearer Token

## Summary
Severity: Critical
Advisory: CVE-2026-74894
Aliases: GHSA-4g2c-wpgj-49w8, PYSEC-2026-3769
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-74894
Type: osv

## Details
openssl_encrypt before 1.4.0 contains an authentication bypass vulnerability in the verify_api_token function that accepts any non-empty Bearer token string without validation. Attackers can upload arbitrary public keys, enumerate all keys, and revoke keys belonging to any user by providing any Bearer token in the Authorization header.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74894.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-4g2c-wpgj-49w8
- https://nvd.nist.gov/vuln/detail/CVE-2026-74894
- https://www.vulncheck.com/advisories/openssl-encrypt-before-authentication-bypass-via-bearer-token
