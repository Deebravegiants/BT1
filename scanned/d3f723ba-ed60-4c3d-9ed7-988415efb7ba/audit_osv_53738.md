# [H] CVE-2023-2176

## Summary
Severity: High
Advisory: CVE-2023-2176
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-04-20
Source: https://osv.dev/vulnerability/CVE-2023-2176
Type: osv

## Details
A vulnerability was found in compare_netdev_and_ip in drivers/infiniband/core/cma.c in RDMA in the Linux Kernel. The improper cleanup results in out-of-boundary read, where a local user can utilize this problem to crash the system or escalation of privilege.

## References
- https://security.netapp.com/advisory/ntap-20230609-0005/
- https://www.spinics.net/lists/linux-rdma/msg114749.html
