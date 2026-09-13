# [M] JLSEC-2026-1125

## Summary
Severity: Medium
Advisory: JLSEC-2026-1125
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1125
Type: osv

## Affected
- Julia: `nats_server_jll` — affected >=0 <2.14.3+0

## Details
NATS-Server is a High-Performance server for NATS.io, a cloud and edge native messaging system. Prior to versions 2.11.15 and 2.12.6, when using ACLs on message subjects, these ACLs were not applied in the `$MQTT.>` namespace, allowing MQTT clients to bypass ACL checks for MQTT subjects. Versions 2.11.15 and 2.12.6 contain a fix. No known workarounds are available.

## References
- https://access.redhat.com/errata/RHSA-2026:21769
- https://access.redhat.com/errata/RHSA-2026:22347
- https://access.redhat.com/errata/RHSA-2026:23345
- https://access.redhat.com/security/cve/CVE-2026-33217
- https://advisories.nats.io/CVE/secnote-2026-07.txt
- https://bugzilla.redhat.com/show_bug.cgi?id=2451446
- https://github.com/nats-io/nats-server/security/advisories/GHSA-jxxm-27vp-c3m5
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-33217.json
