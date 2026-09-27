# [H] NodeBB Pre-Authentication Denial-of-Service

## Summary
Severity: High
Advisory: CVE-2023-30591
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-09-29
Source: https://osv.dev/vulnerability/CVE-2023-30591
Type: osv

## Details
Denial-of-service in NodeBB <= v2.8.10 allows unauthenticated attackers to trigger a crash, when invoking `eventName.startsWith()` or `eventName.toString()`, while processing Socket.IO messages via crafted Socket.IO messages containing array or object type for the event name respectively.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/30xxx/CVE-2023-30591.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-30591
- https://starlabs.sg/advisories/23/23-30591/
- https://github.com/NodeBB/NodeBB/commit/37b48b82a4bc7680c6e4c42647209010cb239c2c
- https://github.com/NodeBB/NodeBB/commit/4d2d76897a02e7068ab74c81d17a2febfae8bfb9
- https://github.com/NodeBB/NodeBB/commit/830f142b7aea2e597294a84d52c05aab3a3539ca
- https://github.com/NodeBB/NodeBB
