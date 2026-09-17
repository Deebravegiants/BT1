# [H] fastify/websocket vulnerable to uncaught exception via crash on malformed packet

## Summary
Severity: High
Advisory: GHSA-4pcg-wr6c-h9cq
CVE: CVE-2022-39386
CWE: CWE-248
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-07
Source: https://github.com/advisories/GHSA-4pcg-wr6c-h9cq
Type: github-advisory

## Affected
- npm: `@fastify/websocket` — affected >=5.0.0 <5.0.1
- npm: `@fastify/websocket` — affected >=6.0.0 <7.1.1
- npm: `fastify-websocket` — affected >=0

## Details
### Impact

Any application using @fastify/websocket could crash if a specific, malformed packet is sent. 

All versions of fastify-websocket are also impacted. That module is deprecated, so it will not be patched.

### Patches

This has been patched in v7.1.1 (fastify v4) and v5.0.1 (fastify v3).

### Workarounds

No known workaround is available. However, it should be possible to attach the error handler manually.
The recommended path is upgrading to the patched versions.

## Credits

[marcolanaro](https://github.com/marcolanaro) for finding and patching this vulnerability

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [@fastify/websocket](https://github.com/fastify/fastify-websocket)
* Email us at [hello@matteocollina.com](mailto:hello@matteocollina.com)

## References
- https://github.com/fastify/fastify-websocket/security/advisories/GHSA-4pcg-wr6c-h9cq
- https://nvd.nist.gov/vuln/detail/CVE-2022-39386
- https://github.com/fastify/fastify-websocket/pull/228
- https://github.com/fastify/fastify-websocket/commit/7e8c41a51c101c3d5ce88caee4f71d9c29eb2863
- https://github.com/fastify/fastify-websocket/commit/c24adeb3efd57a18b2f287c35d029e88b5a47194
- https://github.com/fastify/fastify-websocket
- https://github.com/fastify/fastify-websocket/releases/tag/v5.0.1
- https://github.com/fastify/fastify-websocket/releases/tag/v7.1.1
