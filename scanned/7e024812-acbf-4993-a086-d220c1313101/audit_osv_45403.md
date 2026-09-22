# [H] JLSEC-2026-1126

## Summary
Severity: High
Advisory: JLSEC-2026-1126
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1126
Type: osv

## Affected
- Julia: `nats_server_jll` — affected >=0 <2.14.3+0

## Details
NATS-Server is a High-Performance server for NATS.io, a cloud and edge native messaging system. Prior to versions 2.11.15 and 2.12.6, a client which can connect to the leafnode port can crash the nats-server with a certain malformed message pre-authentication. Versions 2.11.15 and 2.12.6 contain a fix. As a workaround, disable leafnode support if not needed or restrict network connections to the leafnode port, if plausible without compromising the service offered.

## References
- https://access.redhat.com/errata/RHSA-2026:21769
- https://access.redhat.com/errata/RHSA-2026:22347
- https://access.redhat.com/errata/RHSA-2026:23345
- https://access.redhat.com/security/cve/CVE-2026-33218
- https://advisories.nats.io/CVE/secnote-2026-10.txt
- https://bugzilla.redhat.com/show_bug.cgi?id=2451450
- https://github.com/nats-io/nats-server/security/advisories/GHSA-vprv-35vv-q339
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-33218.json
