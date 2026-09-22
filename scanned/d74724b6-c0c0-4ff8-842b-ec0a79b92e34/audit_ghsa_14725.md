# [M] Downloading malicious GitHub Actions workflow artifact results in path traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-2m9h-r57g-45pj
CVE: CVE-2024-54132
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N/U:Green (CVSS_V4)
Published: 2024-12-04
Source: https://github.com/advisories/GHSA-2m9h-r57g-45pj
Type: github-advisory

## Affected
- Go: `github.com/cli/cli/v2` — affected >=0 <2.63.1
- Go: `github.com/cli/cli` — affected >=0

## Details
### Summary

A security vulnerability has been identified in GitHub CLI that could create or overwrite files in unintended directories when users download a malicious GitHub Actions workflow artifact through `gh run download`. 

### Details

This vulnerability stems from a GitHub Actions workflow artifact named `..` when downloaded using `gh run download`.  The artifact name and `--dir` flag are used to determine the artifact’s download path.  When the artifact is named `..`, the resulting files within the artifact are extracted exactly 1 directory higher than the specified `--dir` flag value.

In `2.63.1`, `gh run download` will not download artifacts named `..` and `.` and instead exit with the following error message:

```
error downloading ..: would result in path traversal
```

### Impact

Successful exploitation heightens the risk of local path traversal attack vectors exactly 1 directory higher than intended.

### Remediation and Mitigation

1. Upgrade `gh` to `2.63.1`
2. Implement additional validation to ensure artifact filenames do not contain potentially dangerous patterns, such as `..`, to prevent path traversal risks.

## References
- https://github.com/cli/cli/security/advisories/GHSA-2m9h-r57g-45pj
- https://nvd.nist.gov/vuln/detail/CVE-2024-54132
- https://github.com/cli/cli/commit/1136764c369aaf0cae4ec2ee09dc35d871076932
- https://github.com/cli/cli
