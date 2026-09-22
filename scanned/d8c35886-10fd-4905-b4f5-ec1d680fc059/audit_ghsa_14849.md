# [M] @grpc/grpc-js can allocate memory for incoming messages well above configured limits

## Summary
Severity: Medium
Advisory: GHSA-7v5v-9h63-cj86
CVE: CVE-2024-37168
CWE: CWE-789
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-06-10
Source: https://github.com/advisories/GHSA-7v5v-9h63-cj86
Type: github-advisory

## Affected
- npm: `@grpc/grpc-js` — affected >=1.10.0 <1.10.9
- npm: `@grpc/grpc-js` — affected >=1.9.0 <1.9.15
- npm: `@grpc/grpc-js` — affected >=0 <1.8.22

## Details
### Impact
There are two separate code paths in which memory can be allocated per message in excess of the `grpc.max_receive_message_length` channel option:

 1. If an incoming message has a size on the wire greater than the configured limit, the entire message is buffered before it is discarded.
 2. If an incoming message has a size within the limit on the wire but decompresses to a size greater than the limit, the entire message is decompressed into memory, and on the server is not discarded.

### Patches

This has been patched in versions 1.10.9, 1.9.15, and 1.8.22

## References
- https://github.com/grpc/grpc-node/security/advisories/GHSA-7v5v-9h63-cj86
- https://nvd.nist.gov/vuln/detail/CVE-2024-37168
- https://github.com/grpc/grpc-node/commit/08b0422dae56467ecae1007e899efe66a8c4a650
- https://github.com/grpc/grpc-node/commit/674f4e351a619fd4532f84ae6dff96b8ee4e1ed3
- https://github.com/grpc/grpc-node/commit/a8a020339c7eab1347a343a512ad17a4aea4bfdb
- https://github.com/grpc/grpc-node
