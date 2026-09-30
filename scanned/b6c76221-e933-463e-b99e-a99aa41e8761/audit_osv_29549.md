# [H] wifi: ath12k: fix invalid memory access while processing fragmented packets

## Summary
Severity: High
Advisory: CVE-2024-43847
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-17
Source: https://osv.dev/vulnerability/CVE-2024-43847
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.44, >=6.7.0 <6.10.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath12k: fix invalid memory access while processing fragmented packets

The monitor ring and the reo reinject ring share the same ring mask index.
When the driver receives an interrupt for the reo reinject ring, the
monitor ring is also processed, leading to invalid memory access. Since
monitor support is not yet enabled in ath12k, the ring mask for the monitor
ring should be removed.

Tested-on: QCN9274 hw2.0 PCI WLAN.WBE.1.1.1-00209-QCAHKSWPL_SILICONZ-1

## References
- https://git.kernel.org/stable/c/073f9f249eecd64ab9d59c91c4a23cfdcc02afe4
- https://git.kernel.org/stable/c/36fc66a7d9ca3e5c6eac25362cac63f83df8bed6
- https://git.kernel.org/stable/c/8126f82dab7bd8b2e04799342b19fff0a1fd8575
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43847.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-43847
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
