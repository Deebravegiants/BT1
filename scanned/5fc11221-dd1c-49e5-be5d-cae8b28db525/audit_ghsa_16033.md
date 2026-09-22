# [H] Remote Code Execution in Gogs

## Summary
Severity: High
Advisory: GHSA-phm4-wf3h-pc3r
CVE: CVE-2024-44625
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-11-15
Source: https://github.com/advisories/GHSA-phm4-wf3h-pc3r
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.13.2

## Details
Gogs <0.13.2 is vulnerable to symbolic link path traversal that enables remote code execution via the editFilePost function of internal/route/repo/editor.go.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-44625
- https://fysac.github.io/posts/2024/11/unpatched-remote-code-execution-in-gogs
- https://github.com/gogs/gogs
- https://gogs.io
- https://pkg.go.dev/vuln/GO-2024-3275
