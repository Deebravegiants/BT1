# [M] GoAccess: Heap Out-of-Bounds Write in parse_browser()

## Summary
Severity: Medium
Advisory: CVE-2026-54715
Aliases: GHSA-qcx5-vh2x-35fr
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:L/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-54715
Type: osv

## Details
GoAccess is a real-time web log analyzer and interactive viewer that runs in a terminal in *nix systems or through the browser. In version 1.10.2, parse_browser assumes the matched browser token begins with Opera and moves a trailing version substring to match plus five, allowing a crafted User-Agent in a processed access log to write one to four attacker-influenced bytes beyond the heap allocation and corrupt or crash GoAccess. This issue is fixed in version 1.11.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54715.json
- https://github.com/allinurl/goaccess/security/advisories/GHSA-qcx5-vh2x-35fr
- https://nvd.nist.gov/vuln/detail/CVE-2026-54715
- https://github.com/allinurl/goaccess/commit/81f90d9dafd6956c188dea9f944d24946d3d3351
