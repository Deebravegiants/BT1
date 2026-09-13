# [M] Observable Discrepancy in Argo

## Summary
Severity: Medium
Advisory: GHSA-vj54-cjrx-x696
CVE: CVE-2020-11576
CWE: CWE-203
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-12-09
Source: https://github.com/advisories/GHSA-vj54-cjrx-x696
Type: github-advisory

## Affected
- Go: `github.com/argoproj/argo-cd` — affected >=1.5.0 <1.5.1

## Details
Fixed in v1.5.1, Argo version v1.5.0 was vulnerable to a user-enumeration vulnerability which allowed attackers to determine the usernames of valid (non-SSO) accounts because /api/v1/session returned 401 for an existing username and 404 otherwise.

### Specific Go Packages Affected
github.com/argoproj/argo-cd/util/session
github.com/argoproj/argo-cd/server/session

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-11576
- https://github.com/argoproj/argo-cd/pull/3215
- https://github.com/argoproj/argo-cd/commit/35a7350b7444bcaf53ee0bb11b9d8e3ae4b717a1
- https://www.soluble.ai/blog/argo-cves-2020
