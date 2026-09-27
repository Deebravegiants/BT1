# [H] wifi: ath12k: Fix invalid data access in ath12k_dp_rx_h_undecap_nwifi

## Summary
Severity: High
Advisory: CVE-2025-37943
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-20
Source: https://osv.dev/vulnerability/CVE-2025-37943
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.3.0 <6.6.88, >=6.7.0 <6.12.24, >=6.13.0 <6.13.12, >=6.14.0 <6.14.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: ath12k: Fix invalid data access in ath12k_dp_rx_h_undecap_nwifi

In certain cases, hardware might provide packets with a
length greater than the maximum native Wi-Fi header length.
This can lead to accessing and modifying fields in the header
within the ath12k_dp_rx_h_undecap_nwifi function for
DP_RX_DECAP_TYPE_NATIVE_WIFI decap type and
potentially resulting in invalid data access and memory corruption.

Add a sanity check before processing the SKB to prevent invalid
data access in the undecap native Wi-Fi function for the
DP_RX_DECAP_TYPE_NATIVE_WIFI decap type.

Tested-on: QCN9274 hw2.0 PCI WLAN.WBE.1.3.1-00173-QCAHKSWPL_SILICONZ-1

## References
- https://git.kernel.org/stable/c/3abe15e756481c45f6acba3d476cb3ca4afc3b61
- https://git.kernel.org/stable/c/50be1fb76556e80af9f5da80f28168b6c71bce58
- https://git.kernel.org/stable/c/6ee653194ddb83674913fd2727b8ecfae0597ade
- https://git.kernel.org/stable/c/7f1d986da5c6abb75ffe4d0d325fc9b341c41a1c
- https://git.kernel.org/stable/c/9a0dddfb30f120db3851627935851d262e4e7acb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37943.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37943
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
