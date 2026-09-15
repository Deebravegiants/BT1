# [M] NATS Server: Incomplete Stripping of Nats-Request-Info Header Allows Identity Spoofing

## Summary
Severity: Medium
Advisory: GHSA-pwx7-fx9r-hr4h
CVE: CVE-2026-33223
CWE: CWE-290
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-pwx7-fx9r-hr4h
Type: github-advisory

## Affected
- Go: `github.com/nats-io/nats-server/v2` — affected >=0 <2.11.15
- Go: `github.com/nats-io/nats-server/v2` — affected >=2.12.0-RC.1 <2.12.6
- Go: `github.com/nats-io/nats-server` — affected >=0

## Details
### Background

NATS.io is a high performance open source pub-sub distributed communication technology, built for the cloud, on-premise, IoT, and edge computing.

The nats-server offers a `Nats-Request-Info:` message header, providing information about a request.

### Problem Description

The NATS message header `Nats-Request-Info:` is supposed to be a guarantee of identity by the NATS server, but the stripping of this header from inbound messages was not fully effective.

An attacker with valid credentials for any regular client interface could thus spoof their identity to services which rely upon this header.

### Affected Versions

Any version before v2.12.6 or v2.11.15

### Workarounds

None.

## References
- https://github.com/nats-io/nats-server/security/advisories/GHSA-pwx7-fx9r-hr4h
- https://nvd.nist.gov/vuln/detail/CVE-2026-33223
- https://advisories.nats.io/CVE/secnote-2026-09.txt
- https://github.com/nats-io/nats-server
