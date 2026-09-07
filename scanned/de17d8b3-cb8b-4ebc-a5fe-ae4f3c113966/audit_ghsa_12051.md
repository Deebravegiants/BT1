# [M] NATS: Message tracing can be redirected to arbitrary subject

## Summary
Severity: Medium
Advisory: GHSA-8m2x-3m6q-6w8j
CVE: CVE-2026-33249
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-8m2x-3m6q-6w8j
Type: github-advisory

## Affected
- Go: `github.com/nats-io/nats-server/v2` — affected >=2.11.0 <2.11.15
- Go: `github.com/nats-io/nats-server/v2` — affected >=2.12.0-preview.1 <2.12.6

## Details
### Background

NATS.io is a high performance open source pub-sub distributed communication technology, built for the cloud, on-premise, IoT, and edge computing.

The nats-server supports telemetry on messages, using the per-message NATS headers.

### Problem Description

A valid client which uses message tracing headers can indicate that the trace messages can be sent to an arbitrary valid subject, including those to which the client does not have publish permission.

The payload is a valid trace message and not chosen by the attacker.

### Affected Versions

Any version before v2.12.6 or v2.11.15

### Workarounds

None.

## References
- https://github.com/nats-io/nats-server/security/advisories/GHSA-8m2x-3m6q-6w8j
- https://nvd.nist.gov/vuln/detail/CVE-2026-33249
- https://advisories.nats.io/CVE/secnote-2026-15.txt
- https://github.com/nats-io/nats-server
