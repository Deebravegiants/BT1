# [C] Blueprint Studio API authorization bypass for non-admin Home Assistant users

## Summary
Severity: Critical
Advisory: CVE-2026-53453
Aliases: GHSA-ppwq-ch6x-936g
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-53453
Type: osv

## Details
Blueprint Studio is a VS Code-like file editor for Home Assistant configuration files. Prior to 2.5.2, Blueprint Studio exposed administrator-intended backend API actions to any authenticated Home Assistant user because the backend did not consistently enforce the panel's admin-only authorization boundary. Affected surfaces included the backend API, upload API, stream routes, terminal WebSocket, Blueprint Studio WebSocket subscriptions, call_service, render_template, global_replace, file and stream access paths, upload handling, and terminal helpers. A non-admin user could invoke arbitrary Home Assistant services, expose Home Assistant state through templates, modify configuration files, access streamed or downloaded configuration content, upload files, or reach terminal-related helpers. These actions could compromise the confidentiality, integrity, and availability of the Home Assistant installation. This issue is fixed in version 2.5.2.

## References
- https://github.com/ha-china/blueprint-studio/releases/tag/v2.5.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53453.json
- https://github.com/ha-china/blueprint-studio/security/advisories/GHSA-ppwq-ch6x-936g
- https://nvd.nist.gov/vuln/detail/CVE-2026-53453
- https://github.com/ha-china/blueprint-studio/commit/943aed0be67f3a910b0f70a3864288d5e17e55ce
