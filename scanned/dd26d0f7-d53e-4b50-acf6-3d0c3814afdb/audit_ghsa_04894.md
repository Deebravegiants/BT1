# [H] @grpc/grpc-js: A malformed request can cause a server crash

## Summary
Severity: High
Advisory: GHSA-5375-pq7m-f5r2
CVE: CVE-2026-48068
CWE: CWE-248
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-5375-pq7m-f5r2
Type: github-advisory

## Affected
- npm: `@grpc/grpc-js` — affected >=0 <1.9.16
- npm: `@grpc/grpc-js` — affected >=1.10.0 <1.10.12
- npm: `@grpc/grpc-js` — affected >=1.11.0 <1.11.4
- npm: `@grpc/grpc-js` — affected >=1.12.0 <1.12.7
- npm: `@grpc/grpc-js` — affected >=1.13.0 <1.13.5
- npm: `@grpc/grpc-js` — affected >=1.14.0 <1.14.4

## Details
### Impact
An invalid incoming HTTP/2 stream initiation can cause a server process to crash. This affects all servers created using @grpc/grpc-js.

### Patches
The following version have fixes for this vulnerability:

 - 1.9.16
 - 1.10.12
 - 1.11.4
 - 1.12.7
 - 1.13.5
 - 1.14.4

### Workarounds
There is no workaround.

## References
- https://github.com/grpc/grpc-node/security/advisories/GHSA-5375-pq7m-f5r2
- https://github.com/grpc/grpc-node
- https://github.com/grpc/grpc-node/releases/tag/%40grpc%2Fgrpc-js%401.10.12
- https://github.com/grpc/grpc-node/releases/tag/%40grpc%2Fgrpc-js%401.11.4
- https://github.com/grpc/grpc-node/releases/tag/%40grpc%2Fgrpc-js%401.12.7
- https://github.com/grpc/grpc-node/releases/tag/%40grpc%2Fgrpc-js%401.13.5
- https://github.com/grpc/grpc-node/releases/tag/%40grpc%2Fgrpc-js%401.14.4
- https://github.com/grpc/grpc-node/releases/tag/%40grpc%2Fgrpc-js%401.9.16
