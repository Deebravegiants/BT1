# [H] xsk: Fix corrupted packets for XDP_SHARED_UMEM

## Summary
Severity: High
Advisory: CVE-2022-49972
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-49972
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.16.0 <5.19.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

xsk: Fix corrupted packets for XDP_SHARED_UMEM

Fix an issue in XDP_SHARED_UMEM mode together with aligned mode where
packets are corrupted for the second and any further sockets bound to
the same umem. In other words, this does not affect the first socket
bound to the umem. The culprit for this bug is that the initialization
of the DMA addresses for the pre-populated xsk buffer pool entries was
not performed for any socket but the first one bound to the umem. Only
the linear array of DMA addresses was populated. Fix this by populating
the DMA addresses in the xsk buffer pool for every socket bound to the
same umem.

## References
- https://git.kernel.org/stable/c/2c75891d56ab6fe5ba0d415bfad91d514a4027cd
- https://git.kernel.org/stable/c/58ca14ed98c87cfe0d1408cc65a9745d9e9b7a56
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49972.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49972
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
