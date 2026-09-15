# [M] Open WebUI: Server-side fetches reach blocked and internal hosts via unvalidated HTTP redirect targets

## Summary
Severity: Medium
Advisory: CVE-2026-88001
Aliases: GHSA-5x7x-4c3c-qf5w, PYSEC-2026-3878
CVSS: 5.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-88001
Type: osv

## Details
Open WebUI is an extensible, feature-rich, and user-friendly self-hosted AI platform. From 0.9.5 until 0.11.1, server-side web fetches did not reapply WEB_FETCH_FILTER_LIST or private-address controls to HTTP redirect destinations when AIOHTTP_CLIENT_ALLOW_REDIRECTS was enabled. An authenticated user could redirect the aiohttp and requests fetch paths to excluded hosts, loopback, private networks, or cloud metadata services and route resulting content into web search, URL ingestion, page-fetch tools, or chat image processing. This issue is fixed in version 0.11.1.

## References
- https://github.com/open-webui/open-webui/releases/tag/v0.11.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/88xxx/CVE-2026-88001.json
- https://github.com/open-webui/open-webui/security/advisories/GHSA-5x7x-4c3c-qf5w
- https://nvd.nist.gov/vuln/detail/CVE-2026-88001
- https://github.com/open-webui/open-webui/commit/e3e4bd87df6fc629e7e22081d980d55a7632b8b7
- https://github.com/open-webui/open-webui/pull/27823
