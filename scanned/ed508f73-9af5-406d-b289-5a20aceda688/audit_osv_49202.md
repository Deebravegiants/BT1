# [C] CVE-2018-5703

## Summary
Severity: Critical
Advisory: CVE-2018-5703
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-01-16
Source: https://osv.dev/vulnerability/CVE-2018-5703
Type: osv

## Details
The tcp_v6_syn_recv_sock function in net/ipv6/tcp_ipv6.c in the Linux kernel through 4.14.11 allows attackers to cause a denial of service (slab out-of-bounds write) or possibly have unspecified other impact via vectors involving TLS.

## References
- https://groups.google.com/d/msg/syzkaller-bugs/0PBeVnSzfqQ/5eXAlM46BQAJ
