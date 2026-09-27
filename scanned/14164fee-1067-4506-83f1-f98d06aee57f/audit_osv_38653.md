# [H] FreeScout's client-controlled attachment IDs allow deletion of existing conversation attachments

## Summary
Severity: High
Advisory: CVE-2026-41192
Aliases: GHSA-cv36-2j23-x6g3
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-41192
Type: osv

## Details
FreeScout is a free self-hosted help desk and shared mailbox. Prior to version 1.8.215, the reply and draft flows trust client-supplied encrypted attachment IDs. Any IDs present in `attachments_all[]` but omitted from retained lists are decrypted and passed directly to `Attachment::deleteByIds()`. Because `load_attachments` returns encrypted IDs for attachments on a visible conversation, a mailbox peer can replay those IDs through `save_draft` and delete the original attachment row and file. Version 1.8.215 fixes the vulnerability.

## References
- https://github.com/freescout-help-desk/freescout/releases/tag/1.8.215
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41192.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-cv36-2j23-x6g3
- https://nvd.nist.gov/vuln/detail/CVE-2026-41192
- https://github.com/freescout-help-desk/freescout/commit/5f182818e2391f8e711fec6ae6648ac0b367bef5
