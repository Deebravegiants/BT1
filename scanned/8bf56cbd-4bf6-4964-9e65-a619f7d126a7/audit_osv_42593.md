# [C] LazyOwn: Unauthenticated Socket.IO `input` Event Reaches LazyOwn Command Dispatcher — Unauthenticated RCE

## Summary
Severity: Critical
Advisory: CVE-2026-68502
Aliases: GHSA-fr84-8cfg-59w4
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-68502
Type: osv

## Details
LazyOwn RedTeam/APT Framework is an AI-powered C2 and red-team operations framework. Prior to 0.2.154, LazyOwn's lazyc2.py registers an unauthenticated Socket.IO input event handler that dispatches data.get('value') to LazyOwnShell.one_cmd, reaching LazyOwnShell.do_cmd and subprocess.call(command, shell=True), allowing unauthenticated remote code execution in the C2 process. This issue is fixed in 0.2.154.

## References
- https://github.com/grisuno/LazyOwn/releases/tag/release/0.2.154
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68502.json
- https://github.com/grisuno/LazyOwn/security/advisories/GHSA-fr84-8cfg-59w4
- https://nvd.nist.gov/vuln/detail/CVE-2026-68502
- https://github.com/grisuno/LazyOwn/commit/2e1e3a7b5da8149ae28a970b5883aefa42921652
