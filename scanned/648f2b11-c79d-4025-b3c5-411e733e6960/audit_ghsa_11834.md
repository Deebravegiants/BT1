# [H] NATS has pre-auth server panic via leafnode handling

## Summary
Severity: High
Advisory: GHSA-vprv-35vv-q339
CVE: CVE-2026-33218
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-vprv-35vv-q339
Type: github-advisory

## Affected
- Go: `github.com/nats-io/nats-server/v2` — affected >=0 <2.11.15
- Go: `github.com/nats-io/nats-server/v2` — affected >=2.12.0-RC.1 <2.12.6
- Go: `github.com/nats-io/nats-server` — affected >=0

## Details
### Background

NATS.io is a high performance open source pub-sub distributed communication technology, built for the cloud, on-premise, IoT, and edge computing.

The nats-server allows hub/spoke topologies using "leafnode" connections by other nats-servers.

### Problem Description

A client which can connect to the leafnode port can crash the nats-server with a certain malformed message pre-authentication.

### Affected Versions

Any version before v2.12.6 or v2.11.15

### Workarounds

1. Disable leafnode support if not needed.
2. Restrict network connections to your leafnode port, if plausible without compromising the service offered.

### References

 * This document is canonically: <https://advisories.nats.io/CVE/secnote-2026-10.txt>
 * GHSA advisory: <https://github.com/nats-io/nats-server/security/advisories/GHSA-vprv-35vv-q339>
 * MITRE CVE entry: <https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2026-33218>

## References
- https://github.com/nats-io/nats-server/security/advisories/GHSA-vprv-35vv-q339
- https://nvd.nist.gov/vuln/detail/CVE-2026-33218
- https://advisories.nats.io/CVE/secnote-2026-10.txt
- https://github.com/nats-io/nats-server
