# [H] OpenResty: Buffer overflow when writing PROXY protocol v2 header to upstream

## Summary
Severity: High
Advisory: CVE-2026-55233
Aliases: GHSA-wx83-v28q-68gx
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-07-10
Source: https://osv.dev/vulnerability/CVE-2026-55233
Type: osv

## Details
OpenResty is a high performance web platform. From 1.29.2.1 to before 1.29.2.5, an out-of-bounds write vulnerability exists in the upstream PROXY protocol v2 implementation. When OpenResty is configured to send PROXY protocol version 2 headers to upstream servers, constructing the header in the stream proxy protocol v2 patch can write beyond the bounds of the allocated buffer, causing the worker process to crash and resulting in a denial of service. Only configurations that explicitly enable PROXY protocol v2 for upstream connections are impacted. This issue is fixed in version 1.29.2.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55233.json
- https://github.com/openresty/openresty/security/advisories/GHSA-wx83-v28q-68gx
- https://nvd.nist.gov/vuln/detail/CVE-2026-55233
- https://github.com/openresty/openresty/commit/5c56ad2958a2dad8b2cc99f4987b8642cbc647d1
