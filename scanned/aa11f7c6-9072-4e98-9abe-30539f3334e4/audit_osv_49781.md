# [M] CVE-2019-19056

## Summary
Severity: Medium
Advisory: CVE-2019-19056
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-18
Source: https://osv.dev/vulnerability/CVE-2019-19056
Type: osv

## Details
A memory leak in the mwifiex_pcie_alloc_cmdrsp_buf() function in drivers/net/wireless/marvell/mwifiex/pcie.c in the Linux kernel through 5.3.11 allows attackers to cause a denial of service (memory consumption) by triggering mwifiex_map_pci_memory() failures, aka CID-db8fd2cde932.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/O3PSDE6PTOTVBK2YTKB2TFQP2SUBVSNF/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PY7LJMSPAGRIKABJPDKQDTXYW3L5RX2T/
- http://lists.opensuse.org/opensuse-security-announce/2019-12/msg00029.html
- https://lists.debian.org/debian-lts-announce/2020/01/msg00013.html
- https://lists.debian.org/debian-lts-announce/2020/03/msg00001.html
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://usn.ubuntu.com/4300-1/
- https://usn.ubuntu.com/4301-1/
- https://usn.ubuntu.com/4302-1/
- https://usn.ubuntu.com/4286-1/
- https://usn.ubuntu.com/4286-2/
- https://github.com/torvalds/linux/commit/db8fd2cde93227e566a412cf53173ffa227998bc
