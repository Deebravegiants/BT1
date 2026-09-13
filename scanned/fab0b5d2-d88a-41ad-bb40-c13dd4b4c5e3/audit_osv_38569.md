# [M] FreeScout's cross-user undo reply allows mailbox peers to recall another agent's outbound reply

## Summary
Severity: Medium
Advisory: CVE-2026-40592
Aliases: GHSA-674v-r6xp-mvp6
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-40592
Type: osv

## Details
FreeScout is a free self-hosted help desk and shared mailbox. Prior to version 1.8.214, the undo-send route `GET /conversation/undo-reply/{thread_id}` checks only whether the current user can view the parent conversation. It does not verify that the current user created the reply being undone. In a shared mailbox, one agent can therefore recall another agent's just-sent reply during the 15-second undo window. Version 1.8.214 fixes the vulnerability.

## References
- https://github.com/freescout-help-desk/freescout/releases/tag/1.8.214
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40592.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-674v-r6xp-mvp6
- https://nvd.nist.gov/vuln/detail/CVE-2026-40592
- https://github.com/freescout-help-desk/freescout/commit/c779afdda86fa00a4b85779e034bbfd9ce20c76d
