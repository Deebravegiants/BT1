# [H] wifi: ath12k: Fix invalid entry fetch in ath12k_dp_mon_srng_process

## Summary
Severity: High
Advisory: CVE-2025-37944
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-20
Source: https://osv.dev/vulnerability/CVE-2025-37944
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.88, >=6.7.0 <6.12.25, >=6.13.0 <6.13.12, >=6.14.0 <6.14.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath12k: Fix invalid entry fetch in ath12k_dp_mon_srng_process

Currently, ath12k_dp_mon_srng_process uses ath12k_hal_srng_src_get_next_entry
to fetch the next entry from the destination ring. This is incorrect because
ath12k_hal_srng_src_get_next_entry is intended for source rings, not destination
rings. This leads to invalid entry fetches, causing potential data corruption or
crashes due to accessing incorrect memory locations. This happens because the
source ring and destination ring have different handling mechanisms and using
the wrong function results in incorrect pointer arithmetic and ring management.

To fix this issue, replace the call to ath12k_hal_srng_src_get_next_entry with
ath12k_hal_srng_dst_get_next_entry in ath12k_dp_mon_srng_process. This ensures
that the correct function is used for fetching entries from the destination
ring, preventing invalid memory accesses.

Tested-on: QCN9274 hw2.0 PCI WLAN.WBE.1.3.1-00173-QCAHKSWPL_SILICONZ-1
Tested-on: WCN7850 hw2.0 WLAN.HMT.1.0.c5-00481-QCAHMTSWPL_V1.0_V2.0_SILICONZ-3

## References
- https://git.kernel.org/stable/c/298f0aea5cb32b5038f991f5db201a0fcbb9a31b
- https://git.kernel.org/stable/c/2c512f2eadabb1e80816116894ffaf7d802a944e
- https://git.kernel.org/stable/c/63fdc4509bcf483e79548de6bc08bf3c8e504bb3
- https://git.kernel.org/stable/c/ab7edf42ce800eb34d2f73dd7271b826661a06a5
- https://git.kernel.org/stable/c/b6a3b2b2cead103089d3bb7a57d8209bdfa5399d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37944.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37944
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
