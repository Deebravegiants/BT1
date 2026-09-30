# [H] net: stmmac: Correctly handle Rx checksum offload errors

## Summary
Severity: High
Advisory: CVE-2025-40337
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L)
Published: 2025-12-09
Source: https://osv.dev/vulnerability/CVE-2025-40337
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.2.0 <6.6.117, >=6.7.0 <6.12.58, >=6.13.0 <6.17.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: stmmac: Correctly handle Rx checksum offload errors

The stmmac_rx function would previously set skb->ip_summed to
CHECKSUM_UNNECESSARY if hardware checksum offload (CoE) was enabled
and the packet was of a known IP ethertype.

However, this logic failed to check if the hardware had actually
reported a checksum error. The hardware status, indicating a header or
payload checksum failure, was being ignored at this stage. This could
cause corrupt packets to be passed up the network stack as valid.

This patch corrects the logic by checking the `csum_none` status flag,
which is set when the hardware reports a checksum error. If this flag
is set, skb->ip_summed is now correctly set to CHECKSUM_NONE,
ensuring the kernel's network stack will perform its own validation and
properly handle the corrupt packet.

## References
- https://git.kernel.org/stable/c/1aa319e0f12d2d761a31556b82a5852c98eb0bea
- https://git.kernel.org/stable/c/63fbe0e6413279d5ea5842e2423e351ded547683
- https://git.kernel.org/stable/c/719fcdf29051f7471d5d433475af76219019d33d
- https://git.kernel.org/stable/c/ee0aace5f844ef59335148875d05bec8764e71e8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40337.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40337
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
