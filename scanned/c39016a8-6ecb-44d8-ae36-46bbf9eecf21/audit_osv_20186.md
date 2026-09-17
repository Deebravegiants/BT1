# [M] CVE-2021-32054

## Summary
Severity: Medium
Advisory: CVE-2021-32054
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2021-05-14
Source: https://osv.dev/vulnerability/CVE-2021-32054
Type: osv

## Details
Firely/Incendi Spark before 1.5.5-r4 lacks Content-Disposition headers in certain situations, which may cause crafted files to be delivered to clients such that they are rendered directly in a victim's web browser.

## References
- https://github.com/FirelyTeam/spark/releases/tag/v1.5.5-r4
- https://github.com/FirelyTeam/spark/commit/9c79320059f92d8aa4fbd6cc4fa8f9d5d6ba9941
- https://github.com/FirelyTeam/spark/compare/v1.5.4-r4...v1.5.5-r4
