# [M] NATS is vulnerable to MQTT hijacking via Client ID

## Summary
Severity: Medium
Advisory: GHSA-fcjp-h8cc-6879
CVE: CVE-2026-33215
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:L (CVSS_V3)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-fcjp-h8cc-6879
Type: github-advisory

## Affected
- Go: `github.com/nats-io/nats-server/v2` — affected >=0 <2.11.15
- Go: `github.com/nats-io/nats-server/v2` — affected >=2.12.0-RC.1 <2.12.6

## Details
### Background

NATS.io is a high performance open source pub-sub distributed communication technology, built for the cloud, on-premise, IoT, and edge computing.

The nats-server provides an MQTT client interface.

### Problem Description

Sessions and Messages can by hijacked via MQTT Client ID malfeasance.

### Affected Versions

Any version before v2.12.6 or v2.11.15

### Workarounds

None.

### Resources

 * This document is canonically: <https://advisories.nats.io/CVE/secnote-2026-06.txt>
 * GHSA advisory: <https://github.com/nats-io/nats-server/security/advisories/GHSA-fcjp-h8cc-6879>
 * MITRE CVE entry: <https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2026-33215>

## References
- https://github.com/nats-io/nats-server/security/advisories/GHSA-fcjp-h8cc-6879
- https://nvd.nist.gov/vuln/detail/CVE-2026-33215
- https://advisories.nats.io/CVE/secnote-2026-06.tx
- https://github.com/nats-io/nats-server
- https://pkg.go.dev/vuln/GO-2026-4833
