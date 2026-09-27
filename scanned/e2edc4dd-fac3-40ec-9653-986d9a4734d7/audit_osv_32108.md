# [C] Cacti allows Arbitrary File Creation leading to RCE

## Summary
Severity: Critical
Advisory: CVE-2025-24367
Aliases: GHSA-fxrq-fr7h-9rqq
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-01-27
Source: https://osv.dev/vulnerability/CVE-2025-24367
Type: osv

## Details
Cacti is an open source performance and fault management framework. An authenticated Cacti user can abuse graph creation and graph template functionality to create arbitrary PHP scripts in the web root of the application, leading to remote code execution on the server. This vulnerability is fixed in 1.2.29.

## References
- https://lists.debian.org/debian-lts-announce/2025/02/msg00010.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/24xxx/CVE-2025-24367.json
- https://github.com/Cacti/cacti/security/advisories/GHSA-fxrq-fr7h-9rqq
- https://nvd.nist.gov/vuln/detail/CVE-2025-24367
- https://github.com/Cacti/cacti/commit/c7e4ee798d263a3209ae6e7ba182c7b65284d8f0
