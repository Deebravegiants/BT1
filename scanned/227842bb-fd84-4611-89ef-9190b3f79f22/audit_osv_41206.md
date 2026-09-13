# [H] NATS Server: Remote crash via integer overflow in Connz pagination

## Summary
Severity: High
Advisory: CVE-2026-58207
Aliases: GHSA-q59r-vq66-pxc2
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-07-08
Source: https://osv.dev/vulnerability/CVE-2026-58207
Type: osv

## Details
NATS Server is a high-performance server for NATS.io, the cloud and edge native messaging system. Prior to 2.14.3 and 2.12.12, a client able to send account-scoped connection monitoring requests could crash the server by supplying Connz pagination Offset and Limit values that overflowed internal arithmetic before the response window was safely bounded. This issue is fixed in versions 2.14.3 and 2.12.12.

## References
- https://github.com/nats-io/nats-server/releases/tag/v2.12.12
- https://github.com/nats-io/nats-server/releases/tag/v2.14.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58207.json
- https://github.com/nats-io/nats-server/security/advisories/GHSA-q59r-vq66-pxc2
- https://nvd.nist.gov/vuln/detail/CVE-2026-58207
- https://github.com/nats-io/nats-server/commit/2ae047139e37a38cb01e259a67909e7a39fa38e9
- https://github.com/nats-io/nats-server/commit/894d9411927681d66ce349bf1afe49608dc0c1a3
