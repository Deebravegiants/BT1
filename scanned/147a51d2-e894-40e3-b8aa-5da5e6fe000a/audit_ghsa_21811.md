# [C] Improper Privilege Management in Gitea

## Summary
Severity: Critical
Advisory: GHSA-pg38-r834-g45j
CVE: CVE-2021-45330
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-pg38-r834-g45j
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.6.0

## Details
An issue exsits in Gitea through 1.15.7, which could let a malicious user gain privileges due to client side cookies not being deleted and the session remains valid on the server side for reuse.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45330
- https://github.com/go-gitea/gitea/issues/4336
- https://github.com/go-gitea/gitea/pull/4840
