# [C] Velociraptor Required Permissions bypass by using client monitoring queries

## Summary
Severity: Critical
Advisory: CVE-2026-19583
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-19583
Type: osv

## Details
Velociraptor allows some sensitive artifacts to be gated by additional permissions. For example, the Linux.Sys.BashShell artifact allows arbitrary command execution on endpoints, and so it requires the EXECVE permission to schedule. However, no such check was implemented for client monitoring artifacts. Additionally there was no requirement that client monitoring artifacts carry the CLIENT_EVENTS type. This allows any user who can schedule client monitoring artifacts to also schedule otherwise restricted artifacts (such as Linux.Sys.BashShell).

## References
- http://docs.velociraptor.app/announcements/advisories/cve-2026-19583/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19583.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-19583
- https://github.com/Velocidex/velociraptor/pull/4967
- https://github.com/Velocidex/velociraptor
