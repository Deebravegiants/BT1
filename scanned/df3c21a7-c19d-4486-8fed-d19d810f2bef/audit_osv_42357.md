# [M] FreeRDP before 3.29.0 Out-of-bounds Read via Polygon async message-proxy

## Summary
Severity: Medium
Advisory: CVE-2026-67301
Aliases: GHSA-vxp3-7g6q-rq2w
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-01
Source: https://osv.dev/vulnerability/CVE-2026-67301
Type: osv

## Details
FreeRDP before 3.29.0 contains out-of-bounds read vulnerabilities in the async update message proxy for the PolygonSC and PolygonCB primary drawing orders. When AsyncUpdate is enabled (e.g., xfreerdp /async-update), update_message_PolygonSC() and update_message_PolygonCB() allocate a fresh points array but copy point data from the address of the order structure instead of from polygonSC->points / polygonCB->points, resulting in a client-side out-of-bounds read. A malicious or compromised RDP server sending crafted PolygonSC/PolygonCB update orders can trigger memory disclosure or a client crash.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/67xxx/CVE-2026-67301.json
- https://github.com/FreeRDP/FreeRDP/security/advisories/GHSA-vxp3-7g6q-rq2w
- https://nvd.nist.gov/vuln/detail/CVE-2026-67301
- https://www.vulncheck.com/advisories/freerdp-before-out-of-bounds-read-via-polygon-async-message-proxy
- https://github.com/FreeRDP/FreeRDP/commit/5370fb26fbf034ecd11d3026b6ad639b5fff493f
