# [M] FreeScout's Mailbox OAuth disconnect uses a state-changing GET and is CSRFable

## Summary
Severity: Medium
Advisory: CVE-2026-41194
Aliases: GHSA-6rvw-fhqx-cfv5
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:L/A:L)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-41194
Type: osv

## Details
FreeScout is a free self-hosted help desk and shared mailbox. Prior to version 1.8.215, the mailbox OAuth disconnect action is implemented as `GET /mailbox/oauth-disconnect/{id}/{in_out}/{provider}`. It removes stored OAuth metadata from the mailbox and then redirects. Because it is a GET route, no CSRF token is required and the action can be triggered cross-site against a logged-in mailbox admin. Version 1.8.215 fixes the vulnerability.

## References
- https://github.com/freescout-help-desk/freescout/releases/tag/1.8.215
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41194.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-6rvw-fhqx-cfv5
- https://nvd.nist.gov/vuln/detail/CVE-2026-41194
- https://github.com/freescout-help-desk/freescout/commit/eb397efae2086524ba0ee91abb916de8db7a4ac1
