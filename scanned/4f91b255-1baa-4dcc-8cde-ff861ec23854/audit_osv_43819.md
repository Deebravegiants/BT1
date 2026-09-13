# [M] openssl_encrypt before 1.4.0 Hardcoded Database Credentials

## Summary
Severity: Medium
Advisory: CVE-2026-74891
Aliases: GHSA-v4vm-4xf2-fhqj, PYSEC-2026-3767
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-74891
Type: osv

## Details
openssl_encrypt versions before 1.4.0 contain hardcoded database credentials in standalone server configuration files. Attackers on the same network can access PostgreSQL databases using well-known default credentials to retrieve sensitive data.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74891.json
- https://github.com/jahlives/openssl_encrypt/security/advisories/GHSA-v4vm-4xf2-fhqj
- https://nvd.nist.gov/vuln/detail/CVE-2026-74891
- https://www.vulncheck.com/advisories/openssl-encrypt-before-hardcoded-database-credentials
