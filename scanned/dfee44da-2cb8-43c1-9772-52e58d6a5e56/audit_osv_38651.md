# [H] FreeScout has assigned-only visibility bypass via save_draft that allows hidden conversation draft injection

## Summary
Severity: High
Advisory: CVE-2026-41190
Aliases: GHSA-vj2p-2789-3747
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-41190
Type: osv

## Details
FreeScout is a free self-hosted help desk and shared mailbox. Prior to version 1.8.215, when `APP_SHOW_ONLY_ASSIGNED_CONVERSATIONS` is enabled, direct conversation view correctly blocks users who are neither the assignee nor the creator. The `save_draft` AJAX path is weaker. A direct POST can create a draft inside a conversation that is hidden in the UI. Version 1.8.215 fixes the vulnerability.

## References
- https://github.com/freescout-help-desk/freescout/releases/tag/1.8.215
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41190.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-vj2p-2789-3747
- https://nvd.nist.gov/vuln/detail/CVE-2026-41190
- https://github.com/freescout-help-desk/freescout/commit/414878eb79be7cb01a3ae124df6efcd23729275f
