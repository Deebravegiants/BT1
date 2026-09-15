# [H] Warp Markdown notebook links may open executable local files

## Summary
Severity: High
Advisory: CVE-2026-48704
Aliases: GHSA-589x-4mxh-jcrf
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2026-48704
Type: osv

## Details
Warp is an agentic development environment. From 0.2023.10.24.08.03.stable_00 until 0.2026.05.06.15.42.stable_01, Warp may open executable local files through the operating system default file handler. A malicious Markdown document or project can contain a local-file link that appears as normal rendered content. If a user opens the Markdown in Warp and clicks the link, affected builds may route the resolved local file to a platform file opener instead of limiting the action to safe viewer/editor targets. This vulnerability is fixed in 0.2026.05.06.15.42.stable_01.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48704.json
- https://github.com/warpdotdev/warp/security/advisories/GHSA-589x-4mxh-jcrf
- https://nvd.nist.gov/vuln/detail/CVE-2026-48704
- https://github.com/warpdotdev/warp/commit/7f0c4dd2322198f1b39890f8e6bcdc606c6a3c74
