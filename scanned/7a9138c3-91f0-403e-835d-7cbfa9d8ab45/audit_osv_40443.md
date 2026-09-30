# [C] net: mvpp2: limit XDP frame size to the RX buffer

## Summary
Severity: Critical
Advisory: CVE-2026-53216
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-25
Source: https://osv.dev/vulnerability/CVE-2026-53216
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.9.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.13

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: mvpp2: limit XDP frame size to the RX buffer

mvpp2 has short and long BM pools, and short pool buffers can be smaller
than PAGE_SIZE. The XDP path nevertheless initializes every xdp_buff with
PAGE_SIZE as frame size.

XDP helpers use frame_sz to validate tail growth and to derive the hard
end of the data area. Advertising PAGE_SIZE for short buffers can let
bpf_xdp_adjust_tail() grow a packet past the real allocation, corrupting
memory or later tripping skb tailroom checks.

Initialize the XDP buffer with bm_pool->frag_size so XDP tailroom matches
the actual buffer backing the packet.

## References
- https://git.kernel.org/stable/c/3b8b0c3631b19faee53f0d15a49924129b063eec
- https://git.kernel.org/stable/c/910617a4e67dbdd5fdb39d9dc6a51e491e1b2c3e
- https://git.kernel.org/stable/c/9545cc5ef18ca22d031f2f47c157192460652359
- https://git.kernel.org/stable/c/994bd2b58d2bd08aa97ec0836cc813cfcb00d749
- https://git.kernel.org/stable/c/a3ee9231ccec6ec3be2de89c56f897055fd9eab1
- https://git.kernel.org/stable/c/ec8e1e5842bc0dbd4c272761f4db3651eecd0339
- https://git.kernel.org/stable/c/f3c6aa078927e6fe8121c9c591ddee8716c5305a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53216.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53216
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
