# [M] SiYuan before v3.7.3 Content Disclosure via getBacklinkDoc

## Summary
Severity: Medium
Advisory: CVE-2026-68586
Aliases: GHSA-36v8-mpjm-8j5r, GO-2026-6379
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/CVE-2026-68586
Type: osv

## Details
SiYuan before v3.7.3 fails to apply publish-access filters to the getBacklinkDoc and getBackmentionDoc content endpoints (/api/ref/getBacklinkDoc and /api/ref/getBackmentionDoc). While the corresponding backlink list endpoints filter publish-forbidden documents, the content endpoints (gated only by CheckAuth) do not. A publish-mode reader — including an anonymous reader when publish Basic Auth is disabled — can call these endpoints directly with a publish-forbidden document's ID to retrieve its rendered DOM content and to determine whether the document references a given block (a reference-existence oracle).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68586.json
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-36v8-mpjm-8j5r
- https://nvd.nist.gov/vuln/detail/CVE-2026-68586
- https://www.vulncheck.com/advisories/siyuan-before-content-disclosure-via-getbacklinkdoc
