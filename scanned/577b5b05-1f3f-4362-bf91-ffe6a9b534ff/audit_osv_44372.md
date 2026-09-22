# [C] openssl_encrypt before 1.4.9 Key Substitution via Identity Shadowing

## Summary
Severity: Critical
Advisory: CVE-2026-81706
Aliases: GHSA-8gmx-w9m8-vx7q, PYSEC-2026-3781
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-81706
Type: osv

## Details
openssl_encrypt before 1.4.9 fails to prevent namespace collisions between own identities and contacts in IdentityStore, allowing attackers to create shadowed contact entries invisible until the corresponding own identity is deleted. When the own identity is deleted, the shadowed contact becomes visible and resolves to the attacker's keys, enabling silent key substitution for encrypted files.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/81xxx/CVE-2026-81706.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-8gmx-w9m8-vx7q
- https://nvd.nist.gov/vuln/detail/CVE-2026-81706
- https://www.vulncheck.com/advisories/openssl-encrypt-before-1.4.9-key-substitution-via-identity-shadowing
