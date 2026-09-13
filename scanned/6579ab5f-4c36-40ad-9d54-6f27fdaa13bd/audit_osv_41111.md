# [H] RustDesk Missing Session Scope Enforcement Allows Out-of-Scope Control Message Injection

## Summary
Severity: High
Advisory: CVE-2026-57850
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-57850
Type: osv

## Details
RustDesk before 1.4.9 does not enforce a session's authorized connection scope on the server side, so a peer granted a limited session type (FileTransfer, PortForward, ViewCamera, or Terminal) can send control messages and login options reserved for a full Remote session. An authenticated remote peer can exploit this missing scope check to act outside its granted scope, injecting out-of-scope control messages to observe and control the host beyond the permissions it was given.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/57xxx/CVE-2026-57850.json
- https://github.com/rustdesk/rustdesk/releases/tag/1.4.9
- https://nvd.nist.gov/vuln/detail/CVE-2026-57850
- https://www.vulncheck.com/advisories/rustdesk-missing-session-scope-enforcement-allows-out-of-scope-control-message-injection
- https://github.com/rustdesk/rustdesk/commit/493b14ba78abc3dfb33f109c7f93c1c95a1dabc4
- https://github.com/rustdesk/rustdesk/pull/15469
- https://github.com/rustdesk/rustdesk
- https://github.com/sn0x-sharma/CVE-2026-57850
