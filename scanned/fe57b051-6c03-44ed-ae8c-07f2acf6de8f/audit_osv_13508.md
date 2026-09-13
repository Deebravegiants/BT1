# [M] CVE-2018-20124

## Summary
Severity: Medium
Advisory: CVE-2018-20124
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-12-20
Source: https://osv.dev/vulnerability/CVE-2018-20124
Type: osv

## Details
hw/rdma/rdma_backend.c in QEMU allows guest OS users to trigger out-of-bounds access via a PvrdmaSqWqe ring element with a large num_sge value.

## References
- http://www.securityfocus.com/bid/106290
- https://usn.ubuntu.com/3923-1/
- http://www.openwall.com/lists/oss-security/2018/12/18/2
- https://lists.gnu.org/archive/html/qemu-devel/2018-12/msg02822.html
