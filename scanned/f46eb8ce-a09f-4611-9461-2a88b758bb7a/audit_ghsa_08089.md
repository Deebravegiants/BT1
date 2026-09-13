# [M] nats-server websockets are vulnerable to pre-auth memory DoS

## Summary
Severity: Medium
Advisory: GHSA-qrvq-68c2-7grw
CVE: CVE-2026-27571
CWE: CWE-409, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-qrvq-68c2-7grw
Type: github-advisory

## Affected
- Go: `github.com/nats-io/nats-server/v2` — affected >=0 <2.11.12
- Go: `github.com/nats-io/nats-server/v2` — affected >=2.12.0-RC.1 <2.12.3
- Go: `github.com/nats-io/nats-server` — affected >=0

## Details
### Impact

The WebSockets handling of NATS messages handles compressed messages via the WebSockets negotiated compression.  The implementation bound the memory size of a NATS message but did not independently bound the memory consumption of the memory stream when constructing a NATS message which might then fail validation for size reasons.

An attacker can use a compression bomb to cause excessive memory consumption, often resulting in the operating system terminating the server process.

The use of compression is negotiated before authentication, so this does not require valid NATS credentials to exploit.

The fix was to bounds the decompression to fail once the message was too large, instead of continuing on.

### Patches

This was released in nats-server without being highlighted as a security issue.  It should have been, this was an oversight.  Per the NATS security policy, because this does not require a valid user, it is CVE-worthy.

This was fixed in the v2.11 series with v2.11.12 and in the v2.12 series with v2.12.3.

### Workarounds

This only affects deployments which use WebSockets and which expose the network port to untrusted end-points.

### References

This was reported to the NATS maintainers by Pavel Kohout of Aisle Research (www.aisle.com).

## References
- https://github.com/nats-io/nats-server/security/advisories/GHSA-qrvq-68c2-7grw
- https://nvd.nist.gov/vuln/detail/CVE-2026-27571
- https://github.com/nats-io/nats-server/commit/f77fb7c4535e6727cc1a2899cd8e6bbdd8ba2017
- https://github.com/nats-io/nats-server
- https://github.com/nats-io/nats-server/releases/tag/v2.11.12
- https://github.com/nats-io/nats-server/releases/tag/v2.12.3
- https://pkg.go.dev/vuln/GO-2026-4533
