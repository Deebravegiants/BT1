# [H] rejetto HFS vulnerable to OS Command Execution by remote authenticated users

## Summary
Severity: High
Advisory: GHSA-5f4x-hwv2-w9w2
CVE: CVE-2024-39943
CWE: CWE-284, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-07-05
Source: https://github.com/advisories/GHSA-5f4x-hwv2-w9w2
Type: github-advisory

## Affected
- npm: `hfs` — affected >=0 <0.52.10

## Details
rejetto HFS (aka HTTP File Server) 3 before 0.52.10 on Linux, UNIX, and macOS allows OS command execution by remote authenticated users (if they have Upload permissions). This occurs because a shell is used to execute df (i.e., with execSync instead of spawnSync in child_process in Node.js).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-39943
- https://github.com/rejetto/hfs/commit/305381bd36eee074fb238b64302a252668daad1d
- https://github.com/rejetto/hfs
- https://github.com/rejetto/hfs/compare/v0.52.9...v0.52.10
- https://www.rejetto.com/wiki/index.php/HFS:_Working_with_uploads
