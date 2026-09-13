# [M] Gitea allowed assignment of private issues

## Summary
Severity: Medium
Advisory: GHSA-fhv8-m4j4-cww2
CVE: CVE-2022-38183
CWE: CWE-732
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-08-13
Source: https://github.com/advisories/GHSA-fhv8-m4j4-cww2
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.16.9

## Details
In Gitea before 1.16.9, it was possible for users to add existing issues to projects. Due to improper access controls, an attacker could assign any issue to any project in Gitea (there was no permission check for fetching the issue). As a result, the attacker would get access to private issue titles.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-38183
- https://github.com/go-gitea/gitea/pull/20133
- https://github.com/go-gitea/gitea/pull/20196
- https://blog.gitea.io/2022/07/gitea-1.16.9-is-released
- https://github.com/advisories/GHSA-fhv8-m4j4-cww2
- https://github.com/go-gitea/gitea
- https://herolab.usd.de/security-advisories/usd-2022-0015
- https://pkg.go.dev/vuln/GO-2024-2769
