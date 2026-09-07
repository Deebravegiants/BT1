# [M] NATS  is vulnerable to pre-auth DoS through WebSockets client service

## Summary
Severity: Medium
Advisory: GHSA-8r68-gvr4-jh7j
CVE: CVE-2026-33219
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-8r68-gvr4-jh7j
Type: github-advisory

## Affected
- Go: `github.com/nats-io/nats-server/v2` — affected >=0 <2.11.15
- Go: `github.com/nats-io/nats-server/v2` — affected >=2.12.0-RC.1 <2.12.6
- Go: `github.com/nats-io/nats-server` — affected >=0

## Details
### Background

NATS.io is a high performance open source pub-sub distributed communication technology, built for the cloud, on-premise, IoT, and edge computing.

The nats-server offers a WebSockets client service, used in deployments where browsers are the NATS clients.

### Problem Description

A malicious client which can connect to the WebSockets port can cause unbounded memory use in the nats-server before authentication; this requires sending a corresponding amount of data.

This is a milder variant of [NATS-advisory-ID 2026-02](https://advisories.nats.io/CVE/secnote-2026-02.txt) (aka CVE-2026-27571; GHSA-qrvq-68c2-7grw).
That earlier issue was a compression bomb, this vulnerability is not. Attacks against this new issue thus require significant client bandwidth.

### Affected Versions

Any version before v2.12.6 or v2.11.15

### Workarounds

Disable websockets if not required for project deployment.

## References
- https://github.com/nats-io/nats-server/security/advisories/GHSA-8r68-gvr4-jh7j
- https://nvd.nist.gov/vuln/detail/CVE-2026-33219
- https://advisories.nats.io/CVE/secnote-2026-02.txt
- https://advisories.nats.io/CVE/secnote-2026-11.txt
- https://github.com/advisories/GHSA-qrvq-68c2-7grw
- https://github.com/nats-io/nats-server
