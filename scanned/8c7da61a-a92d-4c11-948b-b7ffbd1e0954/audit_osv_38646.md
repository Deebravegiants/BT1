# [M] FreeScout allows non-folder conversation queries to disclose assigned-only hidden conversations

## Summary
Severity: Medium
Advisory: CVE-2026-41183
Aliases: GHSA-7rh8-9rgv-g35r
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-41183
Type: osv

## Details
FreeScout is a free self-hosted help desk and shared mailbox. Prior to version 1.8.215, the assigned-only restriction is applied to direct conversation view and folder queries, but not to non-folder query builders. Global search and the AJAX filter path still reveal conversations that should be hidden. Version 1.8.215 fixes the vulnerability.

## References
- https://github.com/freescout-help-desk/freescout/releases/tag/1.8.215
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41183.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-7rh8-9rgv-g35r
- https://nvd.nist.gov/vuln/detail/CVE-2026-41183
- https://github.com/freescout-help-desk/freescout/commit/6583d6f5a593b51223904f9e0f2e721e63c76de0
