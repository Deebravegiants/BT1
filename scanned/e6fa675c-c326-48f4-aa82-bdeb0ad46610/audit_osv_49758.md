# [M] CVE-2019-18806

## Summary
Severity: Medium
Advisory: CVE-2019-18806
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-07
Source: https://osv.dev/vulnerability/CVE-2019-18806
Type: osv

## Details
A memory leak in the ql_alloc_large_buffers() function in drivers/net/ethernet/qlogic/qla3xxx.c in the Linux kernel before 5.3.5 allows local users to cause a denial of service (memory consumption) by triggering pci_dma_mapping_error() failures, aka CID-1acb8f2a7a9f.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.5
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=1acb8f2a7a9f10543868ddd737e37424d5c36cf4
