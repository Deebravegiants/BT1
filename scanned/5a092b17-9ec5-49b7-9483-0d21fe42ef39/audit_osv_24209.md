# [M] wifi: ath11k: mhi: fix potential memory leak in ath11k_mhi_register()

## Summary
Severity: Medium
Advisory: CVE-2022-50418
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2022-50418
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.17.0 <5.19.17, >=5.20.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath11k: mhi: fix potential memory leak in ath11k_mhi_register()

mhi_alloc_controller() allocates a memory space for mhi_ctrl. When gets
some error, mhi_ctrl should be freed with mhi_free_controller(). But
when ath11k_mhi_read_addr_from_dt() fails, the function returns without
calling mhi_free_controller(), which will lead to a memory leak.

We can fix it by calling mhi_free_controller() when
ath11k_mhi_read_addr_from_dt() fails.

## References
- https://git.kernel.org/stable/c/015ced9eb63b8b19cb725a1d592d150b60494ced
- https://git.kernel.org/stable/c/43e7c3505ec70db3d3c6458824d5fa40f62e3e7b
- https://git.kernel.org/stable/c/72ef896e80b6ec7cdc1dd42577045f8e7c9c32b3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50418.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50418
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
