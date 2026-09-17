# [H] Evil-WinRM - Path Traversal in download_dir() Function

## Summary
Severity: High
Advisory: CVE-2026-55201
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:A/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-06-17
Source: https://osv.dev/vulnerability/CVE-2026-55201
Type: osv

## Details
Evil-WinRM through 3.9, fixed in commit 6ecd570, contains a path traversal vulnerability in the download_dir() function that allows a rogue or compromised remote Windows server to write files outside the intended download directory by returning filenames with traversal sequences from Get-ChildItem command output that are passed unsanitized to File.join(). Attackers controlling the remote server can exploit this to overwrite sensitive client-side files such as SSH authorized_keys or shell configuration files, achieving persistent access or privilege escalation on the client machine.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55201.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-55201
- https://www.vulncheck.com/advisories/evil-winrm-path-traversal-in-download-dir-function
- https://github.com/Hackplayers/evil-winrm/pull/81
- https://github.com/Hackplayers/evil-winrm/commit/6ecd570a298562dc72ad73978307eb34182f5850
- https://github.com/Hackplayers/evil-winrm
