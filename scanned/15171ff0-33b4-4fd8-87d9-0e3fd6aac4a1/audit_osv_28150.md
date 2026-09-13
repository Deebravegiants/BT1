# [M] Cross-site websocket hijacking in Querybook

## Summary
Severity: Medium
Advisory: CVE-2024-28251
Aliases: GHSA-5349-j4c9-x767
CVSS: 5.6 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-03-13
Source: https://osv.dev/vulnerability/CVE-2024-28251
Type: osv

## Details
Querybook is a Big Data Querying UI, combining collocated table metadata and a simple notebook interface. Querybook's datadocs functionality works by using a Websocket Server. The client talks to this WSS whenever updating/deleting/reading any cells as well as for watching the live status of query executions. Currently the CORS setting allows all origins, which could result in cross-site websocket hijacking and allow attackers to read/edit/remove datadocs of the user. This issue has been addressed in version 3.32.0. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/28xxx/CVE-2024-28251.json
- https://github.com/pinterest/querybook/security/advisories/GHSA-5349-j4c9-x767
- https://nvd.nist.gov/vuln/detail/CVE-2024-28251
- https://github.com/pinterest/querybook/pull/1425
