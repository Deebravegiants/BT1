# [H] Acknowledgement extension out of memory

## Summary
Severity: High
Advisory: GHSA-cqgj-h8vf-4w59
CVE: CVE-2025-53114
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-cqgj-h8vf-4w59
Type: github-advisory

## Affected
- Maven: `org.cometd.java:cometd-java-server-common` — affected >=5.0.0 <5.0.23
- Maven: `org.cometd.java:cometd-java-server-common` — affected >=6.0.0 <6.0.19
- Maven: `org.cometd.java:cometd-java-server-common` — affected >=7.0.0 <7.0.19
- Maven: `org.cometd.java:cometd-java-server-common` — affected >=8.0.0 <8.0.9

## Details
### Impact
Bad clients that always send a fixed batch value while the server is using the acknowledgement extension can cause the unacknowledged message queue to grow indefinitely, eventually resulting in an OutOfMemoryError.

Such bad clients would always send:

```json
{
  "channel": "/meta/connect",
  ...
  "ext": { "ack": 1 }
}
```

The server would never clear the unacknowledged message queue, and one bad client can cause a server outage.

### Patches
5.0.x - https://github.com/cometd/cometd/pull/2168
6.0.x - https://github.com/cometd/cometd/pull/2169
8.0.x - https://github.com/cometd/cometd/pull/2118

### Workarounds
Disable the acknowledgement extension.

### Resources
https://github.com/cometd/cometd/discussions/2116
https://github.com/cometd/cometd/issues/2117

## References
- https://github.com/cometd/cometd/security/advisories/GHSA-cqgj-h8vf-4w59
- https://github.com/cometd/cometd/issues/2117
- https://github.com/cometd/cometd/pull/2118
- https://github.com/cometd/cometd/pull/2168
- https://github.com/cometd/cometd/pull/2169
- https://github.com/cometd/cometd
- https://github.com/cometd/cometd/discussions/2116
