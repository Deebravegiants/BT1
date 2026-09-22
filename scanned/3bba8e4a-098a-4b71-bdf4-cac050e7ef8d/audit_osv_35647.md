# [C] SQL Injection in Raytha CMS

## Summary
Severity: Critical
Advisory: CVE-2026-12076
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/CVE-2026-12076
Type: osv

## Details
Raytha CMS is vulnerable to SQL Injection within the OData filter parsing pipeline.  The vulnerability allows a remote, unauthenticated attacker to execute 
arbitrary SQL statements against the underlying PostgreSQL database, 
leading to full database compromise, including credential extraction.

Because vendor contact attempts were unsuccessful, the vulnerability has only been confirmed in version 1.5.2 but may also affect other versions.

## References
- https://cert.pl/posts/2026/06/CVE-2026-12076
- https://raytha.com
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12076.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-12076
- https://github.com/raythahq/raytha
