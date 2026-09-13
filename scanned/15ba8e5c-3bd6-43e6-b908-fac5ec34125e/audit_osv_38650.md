# [H] FreeScout has assigned-only visibility bypass that allows editing hidden customer-authored threads

## Summary
Severity: High
Advisory: CVE-2026-41189
Aliases: GHSA-4h5p-7f5c-q7gj
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-41189
Type: osv

## Details
FreeScout is a free self-hosted help desk and shared mailbox. Prior to version 1.8.215, customer-thread editing is authorized through `ThreadPolicy::edit()`, which checks mailbox access but does not apply the assigned-only restriction from `ConversationPolicy`. A user who cannot view a conversation can still load and edit customer-authored threads inside it. Version 1.8.215 fixes the vulnerability.

## References
- https://github.com/freescout-help-desk/freescout/releases/tag/1.8.215
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41189.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-4h5p-7f5c-q7gj
- https://nvd.nist.gov/vuln/detail/CVE-2026-41189
- https://github.com/freescout-help-desk/freescout/commit/cdadaf621bb1e1d017315df20d743671f7eae7a9
