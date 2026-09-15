# [M] Cacti has a SQL Injection vulnerability when request automation devices

## Summary
Severity: Medium
Advisory: CVE-2024-54145
Aliases: GHSA-fh3x-69rr-qqpp
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2025-01-27
Source: https://osv.dev/vulnerability/CVE-2024-54145
Type: osv

## Details
Cacti is an open source performance and fault management framework. Cacti has a SQL injection vulnerability in the get_discovery_results function of automation_devices.php using the network parameter. This vulnerability is fixed in 1.2.29.

## References
- https://lists.debian.org/debian-lts-announce/2025/02/msg00010.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/54xxx/CVE-2024-54145.json
- https://github.com/Cacti/cacti/security/advisories/GHSA-fh3x-69rr-qqpp
- https://nvd.nist.gov/vuln/detail/CVE-2024-54145
- https://github.com/Cacti/cacti/commit/c7e4ee798d263a3209ae6e7ba182c7b65284d8f0
