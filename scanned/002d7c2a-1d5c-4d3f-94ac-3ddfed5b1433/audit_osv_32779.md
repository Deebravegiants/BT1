# [C] net: ethernet: mtk_eth_soc: fix SER panic with 4GB+ RAM

## Summary
Severity: Critical
Advisory: CVE-2025-37935
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-05-20
Source: https://osv.dev/vulnerability/CVE-2025-37935
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.90, >=6.7.0 <6.12.28, >=6.13.0 <6.14.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ethernet: mtk_eth_soc: fix SER panic with 4GB+ RAM

If the mtk_poll_rx() function detects the MTK_RESETTING flag, it will
jump to release_desc and refill the high word of the SDP on the 4GB RFB.
Subsequently, mtk_rx_clean will process an incorrect SDP, leading to a
panic.

Add patch from MediaTek's SDK to resolve this.

## References
- https://git.kernel.org/stable/c/317013d1ad13524be02d60b9e98f08fbd13f8c14
- https://git.kernel.org/stable/c/67619cf69dec5d1d7792808dfa548616742dd51d
- https://git.kernel.org/stable/c/6e0490fc36cdac696f96e57b61d93b9ae32e0f4c
- https://git.kernel.org/stable/c/cb625f783f70dc6614f03612b8e64ad99cb0a13c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/37xxx/CVE-2025-37935.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-37935
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
