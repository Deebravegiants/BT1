# [M] NATS has mTLS verify_and_map authentication bypass via incorrect Subject DN matching

## Summary
Severity: Medium
Advisory: GHSA-3f24-pcvm-5jqc
CVE: CVE-2026-33248
CWE: CWE-287, CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-3f24-pcvm-5jqc
Type: github-advisory

## Affected
- Go: `github.com/nats-io/nats-server/v2` — affected >=0 <2.11.15
- Go: `github.com/nats-io/nats-server/v2` — affected >=2.12.0-RC.1 <2.12.6
- Go: `github.com/nats-io/nats-server` — affected >=0

## Details
### Background

NATS.io is a high performance open source pub-sub distributed communication technology, built for the cloud, on-premise, IoT, and edge computing.

One authentication model supported is mTLS, deriving the NATS client identity from properties of the TLS Client Certificate.

### Problem Description

When using mTLS for client identity, with `verify_and_map` to derive a NATS identity from the client certificate's Subject DN, certain patterns of RDN would not be correctly enforced, allowing for authentication bypass.

This does require a valid certificate from a CA already trusted for client certificates, and `DN` naming patterns which the NATS maintainers consider highly unlikely.

So this is an unlikely attack. Nonetheless, administrators who have been very sophisticated in their `DN` construction patterns might conceivably be impacted.

### Affected Versions

Fixed in nats-server 2.12.6 & 2.11.15

### Workarounds

Developers should review their CA issuing practices.

## References
- https://github.com/nats-io/nats-server/security/advisories/GHSA-3f24-pcvm-5jqc
- https://nvd.nist.gov/vuln/detail/CVE-2026-33248
- https://advisories.nats.io/CVE/secnote-2026-13.txt
- https://github.com/nats-io/nats-server
