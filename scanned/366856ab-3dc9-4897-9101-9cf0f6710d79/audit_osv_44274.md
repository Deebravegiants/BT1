# [C] ipvs: do not propagate one-packet flag to synced conns

## Summary
Severity: Critical
Advisory: CVE-2026-80714
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-28
Source: https://osv.dev/vulnerability/CVE-2026-80714
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.36 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.151, >=6.7.0 <6.12.103, >=6.13.0 <6.18.44, >=6.19.0 <7.1.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipvs: do not propagate one-packet flag to synced conns

Synced connections can be created before their destination exists. When
the destination is later added, ip_vs_bind_dest() copies connection flags
from the destination into cp->flags.

IP_VS_CONN_F_ONE_PACKET connections are not synced. If a synced
connection inherits IP_VS_CONN_F_ONE_PACKET while it is already hashed,
expiry can treat it as a one-packet connection and skip unlinking the
existing conn_tab node, leaving stale hash nodes pointing at a freed
struct ip_vs_conn.

Drop IP_VS_CONN_F_ONE_PACKET from destination flags when binding synced
connections.

## References
- https://git.kernel.org/stable/c/06d1d9b56ef8132fbf85006885eb43d9510b8b02
- https://git.kernel.org/stable/c/300348e3ba1521b003d59825f97e24f9a6859688
- https://git.kernel.org/stable/c/44af98cc7d5ef8e730488d5df1eecd5deeaa5947
- https://git.kernel.org/stable/c/4649e6faeecdc2d44bfa6ccbe405eef27e55d816
- https://git.kernel.org/stable/c/a63d2dbaeb50a85d4c976b15a36e6b0c7113db5b
- https://git.kernel.org/stable/c/acbdc276091b308ca7794acb86e761f8203e2f59
- https://git.kernel.org/stable/c/b5ee5b266f833601ac4817f6df0bc496fc376a28
- https://git.kernel.org/stable/c/e7acfc990c29890c883d0d0ce3f737d003a43b44
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/80xxx/CVE-2026-80714.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-80714
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
