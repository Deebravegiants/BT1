# [M] JLSEC-2026-1119

## Summary
Severity: Medium
Advisory: JLSEC-2026-1119
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-03
Source: https://osv.dev/vulnerability/JLSEC-2026-1119
Type: osv

## Affected
- Julia: `nats_server_jll` — affected >=0 <2.10.18+0

## Details
NATS nats-server before 2.9.23 and 2.10.x before 2.10.2 has an authentication bypass. An implicit `$G` user in an authorization block can sometimes be used for unauthenticated access, even when the intention of the configuration was for each user to have an account. The earliest affected version is 2.2.0.

## References
- http://www.openwall.com/lists/oss-security/2023/10/30/1
- http://www.openwall.com/lists/oss-security/2023/10/30/1
- https://github.com/nats-io/nats-server/security/advisories/GHSA-fr2g-9hjm-wr23
- https://github.com/nats-io/nats-server/security/advisories/GHSA-fr2g-9hjm-wr23
- https://www.openwall.com/lists/oss-security/2023/10/13/2
- https://www.openwall.com/lists/oss-security/2023/10/13/2
