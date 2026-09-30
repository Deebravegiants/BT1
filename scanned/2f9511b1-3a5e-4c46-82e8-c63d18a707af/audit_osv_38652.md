# [H] FreeScout's signature only mailbox permission allows unauthorized mailbox chat setting changes

## Summary
Severity: High
Advisory: CVE-2026-41191
Aliases: GHSA-wpv9-c2gv-2j82
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-41191
Type: osv

## Details
FreeScout is a free self-hosted help desk and shared mailbox. Prior to version 1.8.215, `MailboxesController::updateSave()` persists `chat_start_new` outside the allowed-field filter. A user with only the mailbox `sig` permission sees only the signature field in the UI, but can still change the hidden mailbox-wide chat setting via direct POST. Version 1.8.215 fixes the vulnerability.

## References
- https://github.com/freescout-help-desk/freescout/releases/tag/1.8.215
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41191.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-wpv9-c2gv-2j82
- https://nvd.nist.gov/vuln/detail/CVE-2026-41191
- https://github.com/freescout-help-desk/freescout/commit/fb130de64e1c830d85dd6988eaa08d725a7be954
