# [H] NATS has MQTT plaintext password disclosure

## Summary
Severity: High
Advisory: GHSA-v722-jcv5-w7mc
CVE: CVE-2026-33216
CWE: CWE-256
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-v722-jcv5-w7mc
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

For MQTT deployments using usercodes/passwords: MQTT passwords are incorrectly classified as a non-authenticating identity statement (JWT) and exposed via monitoring endpoints.

### Affected Versions

Any version before v2.12.6 or v2.11.15

### Workarounds

Ensure monitoring end-points are adequately secured.

Best practice remains to not expose the monitoring endpoint to the Internet or other untrusted network users.

## References
- https://github.com/nats-io/nats-server/security/advisories/GHSA-v722-jcv5-w7mc
- https://nvd.nist.gov/vuln/detail/CVE-2026-33216
- https://github.com/nats-io/nats-server/commit/b5b63cfc35a57075e09c1f57503d31721bed8099
- https://advisories.nats.io/CVE/secnote-2026-05.txt
- https://github.com/nats-io/nats-server
