# [M] CVE-2022-3435

## Summary
Severity: Medium
Advisory: CVE-2022-3435
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-10-08
Source: https://osv.dev/vulnerability/CVE-2022-3435
Type: osv

## Details
A vulnerability classified as problematic has been found in Linux Kernel. This affects the function fib_nh_match of the file net/ipv4/fib_semantics.c of the component IPv4 Handler. The manipulation leads to out-of-bounds read. It is possible to initiate the attack remotely. It is recommended to apply a patch to fix this issue. The identifier VDB-210357 was assigned to this vulnerability.

## References
- https://lore.kernel.org/netdev/20221005181257.8897-1-dsahern%40kernel.org/T/#u
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GGHENNMLCWIQV2LLA56BJNFIUZ7WB4IY/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/S2KTU5LFZNQS7YNGE56MT46VHMXL3DD2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/VNN3VFQPECS6D4PS6ZWD7AFXTOSJDSSR/
- https://lists.debian.org/debian-lts-announce/2022/12/msg00031.html
- https://vuldb.com/?id.210357
