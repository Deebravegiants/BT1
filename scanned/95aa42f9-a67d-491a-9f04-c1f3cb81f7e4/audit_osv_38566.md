# [H] FreeScout has Customer Edit Cross-Mailbox Email Takeover

## Summary
Severity: High
Advisory: CVE-2026-40589
Aliases: GHSA-mv55-3mgv-fxwr
CVSS: 7.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:L)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-40589
Type: osv

## Details
FreeScout is a free self-hosted help desk and shared mailbox. Prior to version 1.8.214, a low-privileged agent can edit a visible customer and add an email address already owned by a hidden customer in another mailbox. The server discloses the hidden customer’s name and profile URL in the success flash, reassigns the hidden email to the visible customer, and rebinds hidden-mailbox conversations for that email to the visible customer. Version 1.8.214 fixes the issue.

## References
- https://github.com/freescout-help-desk/freescout/releases/tag/1.8.214
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40589.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-mv55-3mgv-fxwr
- https://nvd.nist.gov/vuln/detail/CVE-2026-40589
- https://github.com/freescout-help-desk/freescout/commit/2e2fe37111d92ac665b9ad8806eac94a1a3e502c
