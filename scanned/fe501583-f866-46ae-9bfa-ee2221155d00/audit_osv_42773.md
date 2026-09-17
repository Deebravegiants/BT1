# [H] backmeup (npm) - OS Command Injection via Backup Option Values

## Summary
Severity: High
Advisory: CVE-2026-71243
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-71243
Type: osv

## Details
The backmeup npm package assembles shell command strings by directly concatenating its option values (name, source, destination, filter) - e.g. cmd = "mkdir -p " + path.join(info.destination, info.name) + "; " - and executes the resulting string through a shell via ssh2-exec (locally via child_process, or remotely via SSH when an ssh handle is supplied), rather than using execFile/spawn with an argument array.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71243.json
- https://github.com/adaltas/node-backmeup
- https://nvd.nist.gov/vuln/detail/CVE-2026-71243
