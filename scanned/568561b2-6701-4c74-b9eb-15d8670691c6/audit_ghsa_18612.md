# [C] MCMS vulnerable SQL injection via the content_title parameter

## Summary
Severity: Critical
Advisory: GHSA-54wc-49qj-5ghj
CVE: CVE-2025-56316
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-10-17
Source: https://github.com/advisories/GHSA-54wc-49qj-5ghj
Type: github-advisory

## Affected
- Maven: `net.mingsoft:ms-mcms` — affected >=5.5.0 <6.0.2

## Details
A SQL injection vulnerability in the content_title parameter of the /cms/content/list endpoint in MCMS 5.5.0 through 6.0.1 allows remote attackers to execute arbitrary SQL queries via unsanitized input in the FreeMarker template rendering.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-56316
- https://github.com/ming-soft/MCMS/commit/35ccbf1e3d38ab6aa178524a47c38dff6b448b59
- https://gist.github.com/Erosion2020/5892757e0c6eeb647a218d1c3b323cff
- https://github.com/ming-soft/MCMS
