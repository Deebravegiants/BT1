# [M] JLSEC-2026-1127

## Summary
Severity: Medium
Advisory: JLSEC-2026-1127
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1127
Type: osv

## Affected
- Julia: `nats_server_jll` — affected >=0 <2.14.3+0

## Details
NATS-Server is a High-Performance server for NATS.io, a cloud and edge native messaging system. Prior to versions 2.11.15 and 2.12.6, a malicious client which can connect to the WebSockets port can cause unbounded memory use in the nats-server before authentication; this requires sending a corresponding amount of data. This is a milder variant of CVE-2026-27571. That earlier issue was a compression bomb, this vulnerability is not. Attacks against this new issue thus require significant client bandwidth. Versions 2.11.15 and 2.12.6 contain a fix. As a workaround, disable websockets if not required for project deployment.

## References
- https://access.redhat.com/errata/RHSA-2026:21769
- https://access.redhat.com/errata/RHSA-2026:22347
- https://access.redhat.com/errata/RHSA-2026:23345
- https://access.redhat.com/security/cve/CVE-2026-33219
- https://advisories.nats.io/CVE/secnote-2026-02.txt
- https://advisories.nats.io/CVE/secnote-2026-11.txt
- https://bugzilla.redhat.com/show_bug.cgi?id=2451445
- https://github.com/advisories/GHSA-qrvq-68c2-7grw
- https://github.com/nats-io/nats-server/security/advisories/GHSA-8r68-gvr4-jh7j
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-33219.json
