# [C] Dockwatch 0.6.567 Unauthenticated OS Command Injection via ajax/compose.php

## Summary
Severity: Critical
Advisory: CVE-2026-58455
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-02
Source: https://osv.dev/vulnerability/CVE-2026-58455
Type: osv

## Details
Dockwatch through 0.6.567 contains an unauthenticated OS command injection vulnerability that allows remote attackers to execute arbitrary shell commands by exploiting a missing exit() after an authentication redirect in loader.php combined with unsanitized input passed to shell_exec() in ajax/compose.php. Attackers can seed the required session flag through the incomplete auth check, then inject arbitrary commands via the composePath POST parameter in the composePull action to achieve full host compromise, facilitated by the standard deployment mounting of the Docker socket.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58455.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-58455
- https://www.vulncheck.com/advisories/dockwatch-unauthenticated-os-command-injection-via-ajax-compose-php
- https://github.com/Notifiarr/dockwatch/pull/135
- https://github.com/Notifiarr/dockwatch
