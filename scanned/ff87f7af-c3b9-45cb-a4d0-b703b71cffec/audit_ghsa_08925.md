# [H] picoclaw is vulnerable to OS command injection via the ExecTool component

## Summary
Severity: High
Advisory: GHSA-cv2p-68f4-f4pw
CVE: CVE-2026-36045
CWE: CWE-78
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-cv2p-68f4-f4pw
Type: github-advisory

## Affected
- Go: `github.com/sipeed/picoclaw` — affected >=0

## Details
picoclaw <=v0.1.2 and earlier is vulnerable to OS command injection via the ExecTool component (pkg/tools/shell.go). The guardCommand() function attempts to restrict shell command execution using a denylist of 8 regular expressions, but the denylist is incomplete.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-36045
- https://github.com/sipeed/picoclaw/commit/01d694b9985a66c3d7119fc9f74ce8ed4f0f21b5
- https://gist.github.com/NucleiAv/41899be6266a9813840301577792ed68
- https://github.com/sipeed/picoclaw
- https://github.com/sipeed/picoclaw/releases/tag/v0.1.2
