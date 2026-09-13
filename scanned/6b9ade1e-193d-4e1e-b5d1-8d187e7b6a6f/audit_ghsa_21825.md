# [C] Gitea Remote Code Execution (RCE)

## Summary
Severity: Critical
Advisory: GHSA-hf6f-jq25-8gq9
CVE: CVE-2018-18926
CWE: CWE-94
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-15
Source: https://github.com/advisories/GHSA-hf6f-jq25-8gq9
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.5.2

## Details
Gitea before 1.5.4 allows remote code execution because it does not properly validate session IDs. This is related to session ID handling in the go-macaron/session code for Macaron.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-18926
- https://github.com/go-gitea/gitea/issues/5140
- https://github.com/go-gitea/gitea/pull/5177
- https://github.com/go-gitea/gitea/commit/aeb5655c25053bdcd7eee94ea37df88468374162
