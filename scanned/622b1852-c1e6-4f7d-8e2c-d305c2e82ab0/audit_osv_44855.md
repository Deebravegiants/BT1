# [M] Open WebUI: Any authenticated user can start a non-terminating request via a folder parent cycle

## Summary
Severity: Medium
Advisory: CVE-2026-87013
Aliases: GHSA-8r35-5x5r-hv74
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-09-09
Source: https://osv.dev/vulnerability/CVE-2026-87013
Type: osv

## Details
Open WebUI is an extensible, feature-rich, and user-friendly self-hosted AI platform. From 0.10.0 until 0.11.1, POST /api/v1/folders/{id}/update/parent allowed a user to place a folder under itself or one of its descendants, while the folder tree walks used by DELETE /api/v1/folders/{id} and POST /api/v1/folders/{id}/read did not track visited folder identifiers. An authenticated user could persist a parent cycle and start a request that consumed CPU and memory indefinitely, with the condition remaining stored until repaired. This issue is fixed in version 0.11.1.

## References
- https://github.com/open-webui/open-webui/releases/tag/v0.11.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/87xxx/CVE-2026-87013.json
- https://github.com/open-webui/open-webui/security/advisories/GHSA-8r35-5x5r-hv74
- https://nvd.nist.gov/vuln/detail/CVE-2026-87013
- https://github.com/open-webui/open-webui/commit/23b3a69bc26839bfa74edd1be6bfa2568ae902f4
- https://github.com/open-webui/open-webui/pull/28748
