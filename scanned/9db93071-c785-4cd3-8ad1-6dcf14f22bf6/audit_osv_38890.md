# [C] CVE-2026-42996

## Summary
Severity: Critical
Advisory: CVE-2026-42996
Aliases: GHSA-98hp-pjp7-w62x
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/S:P/AU:Y/R:U/V:D/RE:M/U:Green)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-42996
Type: osv

## Details
JS8Call through 2.3.1 and JS8Call-improved before 3.0 have a stack-based buffer overflow via a radio transmission of @APRSIS GRID followed by a long Maidenhead locator. This occurs in grid2deg in APRSISClient.cpp.

## References
- https://amateur-radio-resources.sourceforge.io/PDF/JS8APRS.pdf
- https://github.com/js8call/js8call/blob/fd721e8b67eed84cb3c09d018205ab9a53e1a8b1/APRSISClient.cpp#L89-L102
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42996.json
- https://github.com/JS8Call-improved/JS8Call-improved/security/advisories/GHSA-98hp-pjp7-w62x
- https://nvd.nist.gov/vuln/detail/CVE-2026-42996
- https://github.com/JS8Call-improved/JS8Call-improved/commit/a6c7a19b82bbd7c2c0c892576f84d7449e8c7088
