# [C] openssl_encrypt before 1.4.9 ANSI Escape Injection via Identity Email

## Summary
Severity: Critical
Advisory: CVE-2026-81707
Aliases: GHSA-qjr2-x6mr-8xgf
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81707
Type: osv

## Details
openssl_encrypt before 1.4.9 fails to sanitize the email field of imported identity documents, allowing attackers to inject ANSI escape sequences that forge the fingerprint verification line displayed to users. Attackers can deliver a crafted identity bundle through normal contact-exchange flows or keyserver responses to manipulate terminal output and display a fraudulent fingerprint, bypassing the out-of-band verification mechanism that protects against key substitution attacks.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81707.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-qjr2-x6mr-8xgf
- https://nvd.nist.gov/vuln/detail/CVE-2026-81707
- https://www.vulncheck.com/advisories/openssl-encrypt-before-1.4.9-ansi-escape-injection-via-identity-email
