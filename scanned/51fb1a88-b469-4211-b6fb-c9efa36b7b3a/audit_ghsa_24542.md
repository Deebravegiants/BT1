# [M] Gitea XSS Vulnerability in Repository Description

## Summary
Severity: Medium
Advisory: GHSA-hqx2-j33x-9fc4
CVE: CVE-2019-1010314
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-hqx2-j33x-9fc4
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=1.7.2 <1.7.4

## Details
Gitea 1.7.2, 1.7.3 is affected by: Cross Site Scripting (XSS). The impact is: execute JavaScript in victim's browser, when the vulnerable repo page is loaded. The component is: repository's description. The attack vector is: victim must navigate to public and affected repo page.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1010314
- https://github.com/go-gitea/gitea/issues/8717
- https://github.com/go-gitea/gitea/pull/6306
- https://github.com/go-gitea/gitea/pull/6308
- https://github.com/go-gitea/gitea/commit/c7bbfd8f5eb097c6910e142415fcdf48fc3c9814
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.7.4
