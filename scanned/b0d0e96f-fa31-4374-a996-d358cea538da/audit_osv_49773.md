# [M] CVE-2019-19043

## Summary
Severity: Medium
Advisory: CVE-2019-19043
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-18
Source: https://osv.dev/vulnerability/CVE-2019-19043
Type: osv

## Details
A memory leak in the i40e_setup_macvlans() function in drivers/net/ethernet/intel/i40e/i40e_main.c in the Linux kernel through 5.3.11 allows attackers to cause a denial of service (memory consumption) by triggering i40e_setup_channel() failures, aka CID-27d461333459.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PY7LJMSPAGRIKABJPDKQDTXYW3L5RX2T/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/O3PSDE6PTOTVBK2YTKB2TFQP2SUBVSNF/
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://usn.ubuntu.com/4300-1/
- https://github.com/torvalds/linux/commit/27d461333459d282ffa4a2bdb6b215a59d493a8f
