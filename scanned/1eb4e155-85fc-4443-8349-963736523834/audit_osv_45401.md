# [H] JLSEC-2026-1124

## Summary
Severity: High
Advisory: JLSEC-2026-1124
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1124
Type: osv

## Affected
- Julia: `nats_server_jll` — affected >=0 <2.14.3+0

## Details
NATS-Server is a High-Performance server for NATS.io, a cloud and edge native messaging system. Prior to versions 2.11.15 and 2.12.6, for MQTT deployments using usercodes/passwords: MQTT passwords are incorrectly classified as a non-authenticating identity statement (JWT) and exposed via monitoring endpoints. Versions 2.11.14 and 2.12.6 contain a fix. As a workaround, ensure monitoring end-points are adequately secured. Best practice remains to not expose the monitoring endpoint to the Internet or other untrusted network users.

## References
- https://access.redhat.com/errata/RHSA-2026:21769
- https://access.redhat.com/errata/RHSA-2026:22347
- https://access.redhat.com/errata/RHSA-2026:23345
- https://access.redhat.com/security/cve/CVE-2026-33216
- https://advisories.nats.io/CVE/secnote-2026-05.txt
- https://bugzilla.redhat.com/show_bug.cgi?id=2451448
- https://github.com/nats-io/nats-server/commit/b5b63cfc35a57075e09c1f57503d31721bed8099
- https://github.com/nats-io/nats-server/security/advisories/GHSA-v722-jcv5-w7mc
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-33216.json
