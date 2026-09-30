# [H] FreeScout Allows Unauthenticated Access to Legacy Attachment Files

## Summary
Severity: High
Advisory: CVE-2026-48812
Aliases: GHSA-wg74-ww4w-2qpc
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-20
Source: https://osv.dev/vulnerability/CVE-2026-48812
Type: osv

## Details
FreeScout is a free help desk and shared inbox built with PHP's Laravel framework. Prior to version 1.8.221, FreeScout's attachment download route skips token authentication for any attachment whose `token_type` is set to `1` (`TOKEN_TYPE_LEGACY`). Because this route is unauthenticated and the file path is deterministic, an unauthenticated remote attacker can download any attachment that was created by an older version of FreeScout without possessing a valid token or session. Version 1.8.221 contains a fix.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48812.json
- https://github.com/freescout-help-desk/freescout/security/advisories/GHSA-wg74-ww4w-2qpc
- https://nvd.nist.gov/vuln/detail/CVE-2026-48812
- https://github.com/freescout-help-desk/freescout/commit/215241ee2eb73eaa3b47e392599c7dc1b427dc7e
