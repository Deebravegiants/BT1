# [H] Path Traversal in web-node-server

## Summary
Severity: High
Advisory: GHSA-3fwq-qv5v-2wxf
CVE: CVE-2020-36651
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-01-18
Source: https://github.com/advisories/GHSA-3fwq-qv5v-2wxf
Type: github-advisory

## Affected
- npm: `web-node-server` — affected >=0 <0.0.11

## Details
A vulnerability has been found in youngerheart nodeserver and classified as critical. Affected by this vulnerability is an unknown functionality of the file nodeserver.js. The manipulation leads to path traversal. The name of the patch is c4c0f0138ab5afbac58e03915d446680421bde28. It is recommended to apply a patch to fix this issue. The identifier VDB-218461 was assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36651
- https://github.com/youngerheart/nodeserver/pull/6
- https://github.com/youngerheart/nodeserver/commit/c4c0f0138ab5afbac58e03915d446680421bde28
- https://github.com/youngerheart/nodeserver
- https://vuldb.com/?ctiid.218461
- https://vuldb.com/?id.218461
