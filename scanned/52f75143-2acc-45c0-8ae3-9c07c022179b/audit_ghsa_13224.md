# [M] Jodit Editor vulnerable to cross-site scripting

## Summary
Severity: Medium
Advisory: GHSA-95xr-cq6h-vwr3
CVE: CVE-2023-42399
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-09-19
Source: https://github.com/advisories/GHSA-95xr-cq6h-vwr3
Type: github-advisory

## Affected
- npm: `jodit` — affected 4.0.0-beta.86

## Details
Cross Site Scripting vulnerability in xdsoft.net Jodit Editor v.4.0.0-beta.86 allows a remote attacker to obtain sensitive information via the rich text editor component.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-42399
- https://github.com/xdan/jodit/issues/1017
- https://github.com/xdan/jodit
