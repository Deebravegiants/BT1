# [H] CVE-2018-20125

## Summary
Severity: High
Advisory: CVE-2018-20125
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-12-20
Source: https://osv.dev/vulnerability/CVE-2018-20125
Type: osv

## Details
hw/rdma/vmw/pvrdma_cmd.c in QEMU allows attackers to cause a denial of service (NULL pointer dereference or excessive memory allocation) in create_cq_ring or create_qp_rings.

## References
- http://www.securityfocus.com/bid/106298
- https://usn.ubuntu.com/3923-1/
- http://www.openwall.com/lists/oss-security/2018/12/19/3
- https://lists.gnu.org/archive/html/qemu-devel/2018-12/msg02823.html
