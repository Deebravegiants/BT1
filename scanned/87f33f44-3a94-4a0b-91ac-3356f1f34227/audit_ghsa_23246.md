# [M] Gitea XSS Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-5rh7-6gfj-mc87
CVE: CVE-2019-1010261
CWE: CWE-79
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-5rh7-6gfj-mc87
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.7.1

## Details
Gitea 1.7.0 and earlier is affected by: Cross Site Scripting (XSS). The impact is: Attacker is able to have victim execute arbitrary JS in browser. The component is: go-get URL generation - PR to fix: https://github.com/go-gitea/gitea/pull/5905. The attack vector is: victim must open a specifically crafted URL. The fixed version is: 1.7.1 and later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-1010261
- https://github.com/go-gitea/gitea/pull/5905
- https://github.com/go-gitea/gitea
