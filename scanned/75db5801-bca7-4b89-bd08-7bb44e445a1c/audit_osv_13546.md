# [H] CVE-2018-20216

## Summary
Severity: High
Advisory: CVE-2018-20216
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-12-20
Source: https://osv.dev/vulnerability/CVE-2018-20216
Type: osv

## Details
QEMU can have an infinite loop in hw/rdma/vmw/pvrdma_dev_ring.c because return values are not checked (and -1 is mishandled).

## References
- http://www.securityfocus.com/bid/106291
- https://usn.ubuntu.com/3923-1/
- http://www.openwall.com/lists/oss-security/2018/12/19/2
- https://lists.gnu.org/archive/html/qemu-devel/2018-12/msg03052.html
