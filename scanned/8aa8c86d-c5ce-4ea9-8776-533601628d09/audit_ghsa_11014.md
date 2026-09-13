# [H] NATS allows MQTT clients to bypass ACL checks

## Summary
Severity: High
Advisory: GHSA-jxxm-27vp-c3m5
CVE: CVE-2026-33217
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-jxxm-27vp-c3m5
Type: github-advisory

## Affected
- Go: `github.com/nats-io/nats-server/v2` — affected >=0 <2.11.15
- Go: `github.com/nats-io/nats-server/v2` — affected >=2.12.0-RC.1 <2.12.6
- Go: `github.com/nats-io/nats-server` — affected >=0

## Details
### Background

NATS.io is a high performance open source pub-sub distributed communication technology, built for the cloud, on-premise, IoT, and edge computing.

The nats-server provides an MQTT client interface.

### Problem Description

When using ACLs on message subjects, these ACLs were not applied in the `$MQTT.>` namespace, allowing MQTT clients to bypass ACL checks for MQTT subjects.

### Affected Versions

Any version before v2.12.6 or v2.11.15

### Workarounds

None.

## References
- https://github.com/nats-io/nats-server/security/advisories/GHSA-jxxm-27vp-c3m5
- https://nvd.nist.gov/vuln/detail/CVE-2026-33217
- https://advisories.nats.io/CVE/secnote-2026-07.txt
- https://github.com/nats-io/nats-server
