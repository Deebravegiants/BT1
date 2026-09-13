# [H] NATS Server panic via malicious compression on leafnode port

## Summary
Severity: High
Advisory: GHSA-52jh-2xxh-pwh6
CVE: CVE-2026-29785
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-52jh-2xxh-pwh6
Type: github-advisory

## Affected
- Go: `github.com/nats-io/nats-server/v2` — affected >=0 <2.11.14
- Go: `github.com/nats-io/nats-server/v2` — affected >=2.12.0-RC.1 <2.12.5
- Go: `github.com/nats-io/nats-server` — affected >=0

## Details
### Background

NATS.io is a high performance open source pub-sub distributed communication technology, built for the cloud, on-premise, IoT, and edge computing.

When configured to accept leafnode connections (for a hub/spoke topology of multiple nats-servers), then the default configuration allows for negotiating compression; a malicious remote NATS server can trigger a server panic via that compression.

### Problem Description

If the nats-server has the "leafnode" configuration enabled (not default), then anyone who can connect can crash the nats-server by triggering a panic. This happens pre-authentication and requires that compression be enabled (which it is, by default, when leafnodes are used).

Context: a NATS server can form various clustering topologies, including local clusters, and superclusters of clusters, but leafnodes allow for separate administrative domains to link together with limited data communication; eg, a server in a moving vehicle might use a local leafnode for agents to connect to, and sync up to a central service as and when available. The leafnode configuration here is where the central server allows other NATS servers to connect into it, almost like regular NATS clients. Documentation examples typically use port 7422 for leafnode communications.

### Affected Versions

Version 2, prior to v2.11.14 or v2.12.5

### Workarounds

Disable compression on the leafnode port:

```
leafnodes {
  port: 7422
  compression: off
}
```

## References
- https://github.com/nats-io/nats-server/security/advisories/GHSA-52jh-2xxh-pwh6
- https://nvd.nist.gov/vuln/detail/CVE-2026-29785
- https://github.com/nats-io/nats-server/commit/a1488de6f2ba6e666aef0f9cce0016f7f167d6a8
- https://advisories.nats.io/CVE/secnote-2026-04.txt
- https://github.com/nats-io/nats-server
