# [M] OpenSift: Race-prone local persistence could cause state corruption/loss

## Summary
Severity: Medium
Advisory: CVE-2026-27189
Aliases: GHSA-3pmp-j953-whxq
CVSS: 6.6 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:L)
Published: 2026-02-21
Source: https://osv.dev/vulnerability/CVE-2026-27189
Type: osv

## Details
OpenSift is an AI study tool that sifts through large datasets using semantic search and generative AI. Versions 1.1.2-alpha and below, use non-atomic and insufficiently synchronized local JSON persistence flows, potentially causing concurrent operations to lose updates or corrupt local state across sessions/study/quiz/flashcard/wellness/auth stores. This issue has been fixed in version 1.1.3-alpha.

## References
- https://github.com/OpenSift/OpenSift/releases/tag/v1.1.3-alpha
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27189.json
- https://github.com/OpenSift/OpenSift/security/advisories/GHSA-3pmp-j953-whxq
- https://nvd.nist.gov/vuln/detail/CVE-2026-27189
