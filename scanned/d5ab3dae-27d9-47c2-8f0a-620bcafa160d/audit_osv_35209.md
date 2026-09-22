# [M] Cross-Site Request Forgery in Raytha CMS

## Summary
Severity: Medium
Advisory: CVE-2025-69238
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-03-16
Source: https://osv.dev/vulnerability/CVE-2025-69238
Type: osv

## Details
Raytha CMS is vulnerable to Cross-Site Request Forgery across multiple endpoints. Attacker can craft special website, which when visited by the authenticated victim, will automatically send POST request to the endpoint (e. x. deletion of the data) without enforcing token verification. 

This issue was fixed in version 1.4.6.

## References
- https://raytha.com
- https://cert.pl/en/posts/2026/03/CVE-2025-69236
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/69xxx/CVE-2025-69238.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-69238
- https://github.com/raythahq/raytha
