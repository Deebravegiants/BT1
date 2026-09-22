# [H] FreeScout has Predictable Attachment Token that Allows Unauthenticated Private File Download via Brute Force

## Summary
Severity: High
Advisory: CVE-2026-40496
Aliases: GHSA-2783-wxmm-wmwr
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N/E:P)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-40496
Type: osv

## Details
FreeScout is a free self-hosted help desk and shared mailbox. Prior to version 1.8.213, attachment download tokens are generated using a weak and predictable formula: `md5(APP_KEY + attachment_id + size)`. Since attachment_id is sequential and size can be brute-forced in a small range, an unauthenticated attacker can forge valid tokens and download any private attachment without credentials. Version 1.8.213 fixes the issue.

## References
- https://github.com/freescout-help-desk/freescout/releases/tag/1.8.213
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40496.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-2783-wxmm-wmwr
- https://nvd.nist.gov/vuln/detail/CVE-2026-40496
- https://github.com/freescout-help-desk/freescout/commit/dbdf8f2260b43a21818255c70f0b61b9de9cd555
