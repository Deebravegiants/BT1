# [C] Authenticated RCE in Raytha CMS

## Summary
Severity: Critical
Advisory: CVE-2025-15540
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:L/SI:L/SA:L)
Published: 2026-03-16
Source: https://osv.dev/vulnerability/CVE-2025-15540
Type: osv

## Details
"Functions" module in Raytha CMS allows privileged users to write custom code to add functionality to application. Due to a lack of sandboxing or access restrictions, JavaScript code executed through Raytha’s “functions” feature can instantiate .NET components and perform arbitrary operations within the application’s hosting environment.

This issue was fixed in version 1.4.6.

## References
- https://raytha.com
- https://cert.pl/en/posts/2026/03/CVE-2025-69236
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/15xxx/CVE-2025-15540.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-15540
- https://github.com/raythahq/raytha
