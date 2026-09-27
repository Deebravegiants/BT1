# [M] FreeRDP: ClearCodec Glyph Cache Count Desync - Heap OOB Read

## Summary
Severity: Medium
Advisory: CVE-2026-33985
Aliases: GHSA-x6gr-8p7h-5h85
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:N/A:L)
Published: 2026-03-30
Source: https://osv.dev/vulnerability/CVE-2026-33985
Type: osv

## Details
FreeRDP is a free implementation of the Remote Desktop Protocol. Prior to version 3.24.2, pixel data from adjacent heap memory is rendered to screen, potentially leaking sensitive data to the attacker. This issue has been patched in version 3.24.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/33xxx/CVE-2026-33985.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-x6gr-8p7h-5h85
- https://nvd.nist.gov/vuln/detail/CVE-2026-33985
- https://github.com/FreeRDP/FreeRDP/commit/c49d1ad43b8c7b32794d0250f2623c2dccd7ef25
