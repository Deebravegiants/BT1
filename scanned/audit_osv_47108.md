# [M] CVE-2015-8950

## Summary
Severity: Medium
Advisory: CVE-2015-8950
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2016-10-10
Source: https://osv.dev/vulnerability/CVE-2015-8950
Type: osv

## Details
arch/arm64/mm/dma-mapping.c in the Linux kernel before 4.0.3, as used in the ION subsystem in Android and other products, does not initialize certain data structures, which allows local users to obtain sensitive information from kernel memory by triggering a dma_mmap call.

## References
- http://source.android.com/security/bulletin/2016-10-01.html
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.0.3
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=6829e274a623187c24f7cfc0e3d35f25d087fcc5
- https://github.com/torvalds/linux/commit/6829e274a623187c24f7cfc0e3d35f25d087fcc5
- https://source.codeaurora.org/quic/la/kernel/msm-3.10/commit/?id=6e2c437a2d0a85d90d3db85a7471f99764f7bbf8
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=6829e274a623187c24f7cfc0e3d35f25d087fcc5
- https://github.com/torvalds/linux/commit/6829e274a623187c24f7cfc0e3d35f25d087fcc5
- https://source.codeaurora.org/quic/la/kernel/msm-3.10/commit/?id=6e2c437a2d0a85d90d3db85a7471f99764f7bbf8
- http://www.securityfocus.com/bid/93318
