# [M] wifi: mwifiex: avoid possible NULL skb pointer dereference

## Summary
Severity: Medium
Advisory: CVE-2023-53384
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2023-53384
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.7.0 <4.14.326, >=4.15.0 <4.19.295, >=4.20.0 <5.4.257, >=5.5.0 <5.10.195, >=5.11.0 <5.15.132, >=5.16.0 <6.1.53, >=6.2.0 <6.4.16, >=6.5.0 <6.5.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

wifi: mwifiex: avoid possible NULL skb pointer dereference

In 'mwifiex_handle_uap_rx_forward()', always check the value
returned by 'skb_copy()' to avoid potential NULL pointer
dereference in 'mwifiex_uap_queue_bridged_pkt()', and drop
original skb in case of copying failure.

Found by Linux Verification Center (linuxtesting.org) with SVACE.

## References
- https://git.kernel.org/stable/c/0c57f9ad2c3ed43abb764b0247d610ff7fdb7a00
- https://git.kernel.org/stable/c/139d285e7695279f030dbb172e2d0245425c86c6
- https://git.kernel.org/stable/c/231086e6a36316b823654f4535653f22d6344420
- https://git.kernel.org/stable/c/35a7a1ce7c7d61664ee54f5239a1f120ab95a87e
- https://git.kernel.org/stable/c/7e7197e4d6a1bc72a774590d8765909f898be1dc
- https://git.kernel.org/stable/c/bef85d58f7709896ed8426560ad117a73a37762f
- https://git.kernel.org/stable/c/c2509f7c37355e1f0bd5b7087815b845fd383723
- https://git.kernel.org/stable/c/d155c5f64cefacdc6a9a26d40be53ee2903c28ff
- https://git.kernel.org/stable/c/d7fd24b8d1bb54c5bcf583139e11a5e651e0263c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53384.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53384
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
