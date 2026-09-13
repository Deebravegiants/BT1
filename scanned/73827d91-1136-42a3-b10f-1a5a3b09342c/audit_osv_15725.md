# [H] CVE-2019-19069

## Summary
Severity: High
Advisory: CVE-2019-19069
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-11-18
Source: https://osv.dev/vulnerability/CVE-2019-19069
Type: osv

## Details
A memory leak in the fastrpc_dma_buf_attach() function in drivers/misc/fastrpc.c in the Linux kernel before 5.3.9 allows attackers to cause a denial of service (memory consumption) by triggering dma_get_sgtable() failures, aka CID-fc739a058d99.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.3.9
- https://security.netapp.com/advisory/ntap-20191205-0001/
- https://usn.ubuntu.com/4208-1/
- https://github.com/torvalds/linux/commit/fc739a058d99c9297ef6bfd923b809d85855b9a9
