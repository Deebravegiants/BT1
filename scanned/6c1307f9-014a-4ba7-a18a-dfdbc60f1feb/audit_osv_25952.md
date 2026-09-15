# [M] Cap'n Proto WebSocket message can cause crash

## Summary
Severity: Medium
Advisory: CVE-2023-48230
Aliases: GHSA-r89h-f468-62w3
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-11-21
Source: https://osv.dev/vulnerability/CVE-2023-48230
Type: osv

## Details
Cap'n Proto is a data interchange format and capability-based RPC system. In versions 1.0 and 1.0.1, when using the KJ HTTP library with WebSocket compression enabled, a buffer underrun can be caused by a remote peer. The underrun always writes a constant value that is not attacker-controlled, likely resulting in a crash, enabling a remote denial-of-service attack. Most Cap'n Proto and KJ users are unlikely to have this functionality enabled and so unlikely to be affected. Maintainers suspect only the Cloudflare Workers Runtime is affected.

If KJ HTTP is used with WebSocket compression enabled, a malicious peer may be able to cause a buffer underrun on a heap-allocated buffer. KJ HTTP is an optional library bundled with Cap'n Proto, but is not directly used by Cap'n Proto. WebSocket compression is disabled by default. It must be enabled via a setting passed to the KJ HTTP library via `HttpClientSettings` or `HttpServerSettings`. The bytes written out-of-bounds are always a specific constant 4-byte string `{ 0x00, 0x00, 0xFF, 0xFF }`. Because this string is not controlled by the attacker, maintainers believe it is unlikely that remote code execution is possible. However, it cannot be ruled out. This functionality first appeared in Cap'n Proto 1.0. Previous versions are not affected.

This issue is fixed in Cap'n Proto 1.0.1.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/48xxx/CVE-2023-48230.json
- https://github.com/capnproto/capnproto/security/advisories/GHSA-r89h-f468-62w3
- https://nvd.nist.gov/vuln/detail/CVE-2023-48230
- https://github.com/capnproto/capnproto/commit/75c5c1499aa6e7690b741204ff9af91cce526c59
- https://github.com/capnproto/capnproto/commit/e7f22da9c01286a2b0e1e5fbdf3ec9ab3aa128ff
