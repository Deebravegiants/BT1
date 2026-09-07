# [C] Valine code injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-mcvg-g9wx-v5vx
CVE: CVE-2022-38545
CWE: CWE-74, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-09-20
Source: https://github.com/advisories/GHSA-mcvg-g9wx-v5vx
Type: github-advisory

## Affected
- npm: `valine` — affected >=0 <1.5.0

## Details
Valine was discovered to contain a remote code execution (RCE) vulnerability which allows attackers to execute arbitrary code via a crafted POST request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-38545
- https://github.com/xCss/Valine/issues/400
- https://github.com/xCss/Valine/commit/c40826c5816c98d797a6b1ed8b62bddf73ed4f65
- https://github.com/xCss/Valine
- https://github.com/xCss/Valine/releases/tag/v1.5.0
