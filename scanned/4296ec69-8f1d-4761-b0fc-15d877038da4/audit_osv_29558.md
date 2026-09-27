# [H] wifi: ath12k: change DMA direction while mapping reinjected packets

## Summary
Severity: High
Advisory: CVE-2024-43881
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-21
Source: https://osv.dev/vulnerability/CVE-2024-43881
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.44, >=6.7.0 <6.10.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath12k: change DMA direction while mapping reinjected packets

For fragmented packets, ath12k reassembles each fragment as a normal
packet and then reinjects it into HW ring. In this case, the DMA
direction should be DMA_TO_DEVICE, not DMA_FROM_DEVICE. Otherwise,
an invalid payload may be reinjected into the HW and
subsequently delivered to the host.

Given that arbitrary memory can be allocated to the skb buffer,
knowledge about the data contained in the reinjected buffer is lacking.
Consequently, there’s a risk of private information being leaked.

Tested-on: QCN9274 hw2.0 PCI WLAN.WBE.1.1.1-00209-QCAHKSWPL_SILICONZ-1

## References
- https://git.kernel.org/stable/c/33322e3ef07409278a18c6919c448e369d66a18e
- https://git.kernel.org/stable/c/6925320fcd40d8042d32bf4ede8248e7a5315c3b
- https://git.kernel.org/stable/c/e99d9b16ff153de9540073239d24adc3b0a3a997
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43881.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-43881
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
