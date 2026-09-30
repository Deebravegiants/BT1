# [M] CVE-2023-1382

## Summary
Severity: Medium
Advisory: CVE-2023-1382
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-04-19
Source: https://osv.dev/vulnerability/CVE-2023-1382
Type: osv

## Details
A data race flaw was found in the Linux kernel, between where con is allocated and con->sock is set. This issue leads to a NULL pointer dereference when accessing con->sock->sk in net/tipc/topsrv.c in the tipc protocol in the Linux kernel.

## References
- https://lore.kernel.org/netdev/bc7bd3183f1c275c820690fc65b708238fe9e38e.1668807842.git.lucien.xin%40gmail.com/T/#u
