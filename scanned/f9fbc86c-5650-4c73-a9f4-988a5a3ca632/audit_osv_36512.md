# [H] DataEase Vulnerable to Brute-Force Attack on Admin JWT Secret Derived from Password that Enables Full Account Takeover

## Summary
Severity: High
Advisory: CVE-2026-23958
Aliases: GHSA-5wvm-4m4q-rh7j
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2026-01-22
Source: https://osv.dev/vulnerability/CVE-2026-23958
Type: osv

## Details
Dataease is an open source data visualization analysis tool. Prior to version 2.10.19, DataEase uses the MD5 hash of the user’s password as the JWT signing secret. This deterministic secret derivation allows an attacker to brute-force the admin’s password by exploiting unmonitored API endpoints that verify JWT tokens. The vulnerability has been fixed in v2.10.19. No known workarounds are available.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23958.json
- https://github.com/dataease/dataease/security/advisories/GHSA-5wvm-4m4q-rh7j
- https://nvd.nist.gov/vuln/detail/CVE-2026-23958
- https://www.ox.security/blog/blog-dataease-cve-2026-23958-admin-takeover/
