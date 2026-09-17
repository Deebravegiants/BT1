# [M] Denial of service in Valine

## Summary
Severity: Medium
Advisory: GHSA-p2c4-gxp4-j3xp
CVE: CVE-2021-34801
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2021-06-21
Source: https://github.com/advisories/GHSA-p2c4-gxp4-j3xp
Type: github-advisory

## Affected
- npm: `valine` — affected >=0

## Details
Valine is a fast, simple & powerful comment system. Valine 1.4.14 allows remote attackers to cause a denial of service (application outage) by supplying a ua (aka User-Agent) value that only specifies the product and version.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-34801
- https://github.com/xCss/Valine/issues/366
- https://github.com/xCss/Valine
