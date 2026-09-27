# [M] amqp091-go has a Potential Memory Exhaustion/Protocol Violation via Broker-Controlled Oversized Payload

## Summary
Severity: Medium
Advisory: CVE-2026-79921
Aliases: GHSA-6c5v-hqjr-5xxp
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-79921
Type: osv

## Details
amqp091-go is a Go AMQP 0.9.1 client. Before version 1.13.0, a compromised or malicious AMQP broker can force the client to allocate resources for and process content body frames that exceed the negotiated frame_max limit. This can lead to unexpected memory consumption or application-layer denial of service (DoS), bypassing the protocol's built-in framing constraints. Version 1.13.0 contains a fix. No known workarounds are available.

## References
- https://github.com/rabbitmq/amqp091-go/releases/tag/v1.13.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/79xxx/CVE-2026-79921.json
- https://github.com/rabbitmq/amqp091-go/security/advisories/GHSA-6c5v-hqjr-5xxp
- https://nvd.nist.gov/vuln/detail/CVE-2026-79921
- https://github.com/rabbitmq/amqp091-go/commit/6beb7b51f59e46ddcf8066ad498dad32491d3be0
- https://github.com/rabbitmq/amqp091-go/pull/353
