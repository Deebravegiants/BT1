# [C] Cua computer-server before 0.3.42 Unauthenticated RCE via Desktop Control

## Summary
Severity: Critical
Advisory: CVE-2026-86121
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-05
Source: https://osv.dev/vulnerability/CVE-2026-86121
Type: osv

## Details
Cua computer-server versions before 0.3.42 skip authentication when the CONTAINER_NAME environment variable is unset and bind to all interfaces by default, allowing unauthenticated attackers to execute arbitrary commands. Attackers can reach TCP port 8000 to run shell commands via the run_command endpoint, read and write arbitrary files through file operation endpoints, and access interactive PTY shells without authentication.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/86xxx/CVE-2026-86121.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-86121
- https://www.vulncheck.com/advisories/cua-computer-server-before-0.3.42-unauthenticated-rce-via-desktop-control
- https://github.com/trycua/cua/issues/1892
- https://github.com/trycua/cua/commit/59cf25c0ec54
- https://github.com/trycua/cua
- https://github.com/trycua/cua/blob/10a2e71792db/libs/python/computer-server/computer_server/cli.py
- https://github.com/trycua/cua/blob/10a2e71792db/libs/python/computer-server/computer_server/main.py
