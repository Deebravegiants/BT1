# [M] CVE-2020-12465

## Summary
Severity: Medium
Advisory: CVE-2020-12465
CVSS: 6.7 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-04-29
Source: https://osv.dev/vulnerability/CVE-2020-12465
Type: osv

## Details
An array overflow was discovered in mt76_add_fragment in drivers/net/wireless/mediatek/mt76/dma.c in the Linux kernel before 5.5.10, aka CID-b102f0c522cf. An oversized packet with too many rx fragments can corrupt memory of adjacent pages.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.5.10
- https://security.netapp.com/advisory/ntap-20200608-0001/
- https://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=b102f0c522cf668c8382c56a4f771b37d011cda2
- https://github.com/torvalds/linux/commit/b102f0c522cf668c8382c56a4f771b37d011cda2
