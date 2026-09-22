# [H] CVE-2018-20191

## Summary
Severity: High
Advisory: CVE-2018-20191
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-12-20
Source: https://osv.dev/vulnerability/CVE-2018-20191
Type: osv

## Details
hw/rdma/vmw/pvrdma_main.c in QEMU does not implement a read operation (such as uar_read by analogy to uar_write), which allows attackers to cause a denial of service (NULL pointer dereference).

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/CGCFIFSIWUREEQQOZDZFBYKWZHXCWBZN/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KJMTVGDLA654HNCDGLCUEIP36SNJEKK7/
- http://www.securityfocus.com/bid/106276
- https://usn.ubuntu.com/3923-1/
- http://www.openwall.com/lists/oss-security/2018/12/18/1
- https://lists.gnu.org/archive/html/qemu-devel/2018-12/msg03066.html
