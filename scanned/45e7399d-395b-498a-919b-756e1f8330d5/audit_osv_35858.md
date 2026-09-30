# [C] WGDashboard Server-Side Request Forgery Vulnerability

## Summary
Severity: Critical
Advisory: CVE-2026-15732
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-06
Source: https://osv.dev/vulnerability/CVE-2026-15732
Type: osv

## Details
A Server-Side Request Forgery (SSFR) vulnerability exist in WGDashboard version 4.2.3 and earlier. The webhook functionality allows authenticated attackers to make arbitrary HTTP requests and retrieve responses.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15732.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-15732
- https://github.com/Stuub/WGDashboard-v4.3.2-Full-Read-SSRF-via-Webhooks-PoC
- https://github.com/WGDashboard/WGDashboard
