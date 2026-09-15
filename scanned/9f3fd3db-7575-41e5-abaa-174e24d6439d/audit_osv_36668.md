# [H] openITCOCKPIT has Authenticated Command Injection Leading to Remote Code Execution via Host Address Macro Expansion

## Summary
Severity: High
Advisory: CVE-2026-24893
Aliases: GHSA-789q-pw85-j2q2
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-14
Source: https://osv.dev/vulnerability/CVE-2026-24893
Type: osv

## Details
openITCOCKPIT is an open source monitoring tool built for different monitoring engines. openITCOCKPIT Community Edition prior to version 5.5.2 contains a command injection vulnerability that allows an authenticated user with permission to add or modify hosts to execute arbitrary OS commands on the monitoring backend. The vulnerability arises because user-controlled host attributes (specifically the host address) are expanded into monitoring command templates without validation, escaping, or quoting. These templates are later executed by the monitoring engine (Nagios/Icinga) via a shell, resulting in remote code execution. Version 5.5.2 patches the issue.

## References
- https://github.com/openITCOCKPIT/openITCOCKPIT/releases/tag/openITCOCKPIT-5.5.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24893.json
- https://github.com/openITCOCKPIT/openITCOCKPIT/security/advisories/GHSA-789q-pw85-j2q2
- https://nvd.nist.gov/vuln/detail/CVE-2026-24893
- https://openitcockpit.io/blog/posts/2026/2026-04-14-openitcockpit-agent-3.6.0-and-5.5.2
