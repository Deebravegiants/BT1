# [M] JLSEC-2026-1131

## Summary
Severity: Medium
Advisory: JLSEC-2026-1131
Ecosystem: Julia
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1131
Type: osv

## Affected
- Julia: `nats_server_jll` — affected >=0 <2.14.3+0

## Details
NATS-Server is a High-Performance server for NATS.io, a cloud and edge native messaging system. Prior to versions 2.11.15 and 2.12.6, if a nats-server is run with static credentials for all clients provided via argv (the command-line), then those credentials are visible to any user who can see the monitoring port, if that too is enabled. The `/debug/vars` end-point contains an unredacted copy of argv. Versions 2.11.15 and 2.12.6 contain a fix. As a workaround, configure credentials inside a configuration file instead of via argv, and do not enable the monitoring port if using secrets in argv. Best practice remains to not expose the monitoring port to the Internet, or to untrusted network sources.

## References
- https://access.redhat.com/errata/RHSA-2026:21769
- https://access.redhat.com/errata/RHSA-2026:22347
- https://access.redhat.com/errata/RHSA-2026:23345
- https://access.redhat.com/security/cve/CVE-2026-33247
- https://advisories.nats.io/CVE/secnote-2026-14.txt
- https://bugzilla.redhat.com/show_bug.cgi?id=2451486
- https://github.com/nats-io/nats-server/security/advisories/GHSA-x6g4-f6q3-fqvv
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-33247.json
