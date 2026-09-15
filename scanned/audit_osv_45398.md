# [H] JLSEC-2026-1121

## Summary
Severity: High
Advisory: JLSEC-2026-1121
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1121
Type: osv

## Affected
- Julia: `nats_server_jll` — affected >=0 <2.14.3+0

## Details
NATS-Server is a High-Performance server for NATS.io, a cloud and edge native messaging system. Starting in version 2.2.0 and prior to versions 2.11.14 and 2.12.5, a missing sanity check on a WebSockets frame could trigger a server panic in the nats-server.  This happens before authentication, and so is exposed to anyone who can connect to the websockets port. Versions 2.11.14 and 2.12.5 contains a fix. A workaround is available. The vulnerability only affects deployments which use WebSockets and which expose the network port to untrusted end-points. If one is able to do so, a defense in depth of restricting either of these will mitigate the attack.

## References
- https://access.redhat.com/errata/RHSA-2026:21769
- https://access.redhat.com/errata/RHSA-2026:22347
- https://access.redhat.com/errata/RHSA-2026:23345
- https://access.redhat.com/security/cve/CVE-2026-27889
- https://advisories.nats.io/CVE/secnote-2026-03.txt
- https://bugzilla.redhat.com/show_bug.cgi?id=2451447
- https://github.com/nats-io/nats-server/security/advisories/GHSA-pq2q-rcw4-3hr6
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-27889.json
