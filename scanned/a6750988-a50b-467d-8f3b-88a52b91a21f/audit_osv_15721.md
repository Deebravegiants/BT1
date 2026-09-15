# [M] CVE-2019-19054

## Summary
Severity: Medium
Advisory: CVE-2019-19054
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-18
Source: https://osv.dev/vulnerability/CVE-2019-19054
Type: osv

## Details
A memory leak in the cx23888_ir_probe() function in drivers/media/pci/cx23885/cx23888-ir.c in the Linux kernel through 5.3.11 allows attackers to cause a denial of service (memory consumption) by triggering kfifo_alloc() failures, aka CID-a7b2df76b42b.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/O3PSDE6PTOTVBK2YTKB2TFQP2SUBVSNF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PY7LJMSPAGRIKABJPDKQDTXYW3L5RX2T/
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://usn.ubuntu.com/4525-1/
- https://usn.ubuntu.com/4526-1/
- https://usn.ubuntu.com/4527-1/
- http://lists.opensuse.org/opensuse-security-announce/2020-03/msg00021.html
- https://github.com/torvalds/linux/commit/a7b2df76b42bdd026e3106cf2ba97db41345a177
