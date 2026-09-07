# [M] NATS: Leafnode connections allow spoofing of Nats-Request-Info identity headers

## Summary
Severity: Medium
Advisory: GHSA-55h8-8g96-x4hj
CVE: CVE-2026-33246
CWE: CWE-287, CWE-290
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-55h8-8g96-x4hj
Type: github-advisory

## Affected
- Go: `github.com/nats-io/nats-server/v2` — affected >=0 <2.11.15
- Go: `github.com/nats-io/nats-server/v2` — affected >=2.12.0-RC.1 <2.12.6
- Go: `github.com/nats-io/nats-server` — affected >=0

## Details
### Background

NATS.io is a high performance open source pub-sub distributed communication technology, built for the cloud, on-premise, IoT, and edge computing.

The nats-server allows hub/spoke topologies using "leafnode" connections by other nats-servers.  NATS messages can have headers.

### Problem Description

The nats-server offers a `Nats-Request-Info:` message header, providing information about a request.  This is supposed to provide enough information to allow for account/user identification, such that NATS clients could make their own decisions on how to trust a message, provided that they trust the nats-server as a broker.

A leafnode connecting to a nats-server is not fully trusted unless the system account is bridged too.  Thus identity claims should not have propagated unchecked.

Thus NATS clients relying upon the Nats-Request-Info: header could be spoofed.

Does not directly affect the nats-server itself, but the CVSS Confidentiality and Integrity scores are based upon what a hypothetical client might choose to do with this NATS header.

### Affected Versions

Any version before v2.12.6 or v2.11.15

### Workarounds

None.

## References
- https://github.com/nats-io/nats-server/security/advisories/GHSA-55h8-8g96-x4hj
- https://nvd.nist.gov/vuln/detail/CVE-2026-33246
- https://advisories.nats.io/CVE/secnote-2026-08.txt
- https://github.com/nats-io/nats-server
