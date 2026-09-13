# [H] JLSEC-2026-1122

## Summary
Severity: High
Advisory: JLSEC-2026-1122
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1122
Type: osv

## Affected
- Julia: `nats_server_jll` — affected >=0 <2.14.3+0

## Details
NATS-Server is a High-Performance server for NATS.io, a cloud and edge native messaging system. Prior to versions 2.11.14 and 2.12.5, if the nats-server has the "leafnode" configuration enabled (not default), then anyone who can connect can crash the nats-server by triggering a panic. This happens pre-authentication and requires that compression be enabled (which it is, by default, when leafnodes are used). Versions 2.11.14 and 2.12.5 contain a fix. As a workaround, disable compression on the leafnode port.

## References
- https://access.redhat.com/errata/RHSA-2026:21769
- https://access.redhat.com/errata/RHSA-2026:22347
- https://access.redhat.com/errata/RHSA-2026:23345
- https://access.redhat.com/security/cve/CVE-2026-29785
- https://advisories.nats.io/CVE/secnote-2026-04.txt
- https://bugzilla.redhat.com/show_bug.cgi?id=2451444
- https://github.com/nats-io/nats-server/commit/a1488de6f2ba6e666aef0f9cce0016f7f167d6a8
- https://github.com/nats-io/nats-server/security/advisories/GHSA-52jh-2xxh-pwh6
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-29785.json
