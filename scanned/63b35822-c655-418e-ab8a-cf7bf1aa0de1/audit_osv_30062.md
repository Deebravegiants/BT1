# [H] wifi: ath11k: fix array out-of-bound access in SoC stats

## Summary
Severity: High
Advisory: CVE-2024-49930
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-49930
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.6.0 <5.10.227, >=5.11.0 <5.15.168, >=5.16.0 <6.1.113, >=6.2.0 <6.6.55, >=6.7.0 <6.10.14, >=6.11.0 <6.11.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath11k: fix array out-of-bound access in SoC stats

Currently, the ath11k_soc_dp_stats::hal_reo_error array is defined with a
maximum size of DP_REO_DST_RING_MAX. However, the ath11k_dp_process_rx()
function access ath11k_soc_dp_stats::hal_reo_error using the REO
destination SRNG ring ID, which is incorrect. SRNG ring ID differ from
normal ring ID, and this usage leads to out-of-bounds array access. To fix
this issue, modify ath11k_dp_process_rx() to use the normal ring ID
directly instead of the SRNG ring ID to avoid out-of-bounds array access.

Tested-on: QCN9074 hw1.0 PCI WLAN.HK.2.7.0.1-01744-QCAHKSWPL_SILICONZ-1

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-355557.html
- https://git.kernel.org/stable/c/01b77f5ee11c89754fb836af8f76799d3b72ae2f
- https://git.kernel.org/stable/c/0f26f26944035ec67546a944f182cbad6577a9c0
- https://git.kernel.org/stable/c/4dd732893bd38cec51f887244314e2b47f0d658f
- https://git.kernel.org/stable/c/6045ef5b4b00fee3629689f791992900a1c94009
- https://git.kernel.org/stable/c/69f253e46af98af17e3efa3e5dfa72fcb7d1983d
- https://git.kernel.org/stable/c/73e235728e515faccc104b0153b47d0f263b3344
- https://git.kernel.org/stable/c/7a552bc2f3efe2aaf77a85cb34cdf4a63d81a1a7
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/49xxx/CVE-2024-49930.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-49930
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
