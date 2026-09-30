# [M] NATS JetStream has an authorization bypass through its Management API

## Summary
Severity: Medium
Advisory: GHSA-9983-vrx2-fg9c
CVE: CVE-2026-33222
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-9983-vrx2-fg9c
Type: github-advisory

## Affected
- Go: `github.com/nats-io/nats-server/v2` — affected >=0 <2.11.15
- Go: `github.com/nats-io/nats-server/v2` — affected >=2.12.0-RC.1 <2.12.6
- Go: `github.com/nats-io/nats-server` — affected >=0

## Details
### Background

NATS.io is a high performance open source pub-sub distributed communication technology, built for the cloud, on-premise, IoT, and edge computing.

The persistent storage feature, JetStream, has a management API which has many features, amongst which are backup and restore.

### Problem Description

Users with JetStream admin API access to restore one stream could restore to other stream names, impacting data which should have been protected against them.

### Affected Versions

Any version before v2.12.6 or v2.11.15

### Workarounds

If developers have configured users to have limited JetStream restore permissions, temporarily remove those permissions.

## References
- https://github.com/nats-io/nats-server/security/advisories/GHSA-9983-vrx2-fg9c
- https://nvd.nist.gov/vuln/detail/CVE-2026-33222
- https://advisories.nats.io/CVE/secnote-2026-12.txt
- https://github.com/nats-io/nats-server
