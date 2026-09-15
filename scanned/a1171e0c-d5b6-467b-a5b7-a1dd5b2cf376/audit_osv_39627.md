# [H] tun: free page on build_skb failure in tun_xdp_one()

## Summary
Severity: High
Advisory: CVE-2026-46322
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-46322
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

tun: free page on build_skb failure in tun_xdp_one()

When build_skb() fails in tun_xdp_one(), the function sets ret to
-ENOMEM and jumps to the out label, which returns without freeing the
page that vhost_net_build_xdp() allocated for the frame. As with the
short-frame rejection path, tun_sendmsg() discards the per-buffer error
and still returns total_len, so vhost_tx_batch() takes the success path
and never frees the page. Each build_skb() failure in a batch leaks one
page-frag chunk.

Free the page before taking the error path, matching the put_page() the
other error exits of tun_xdp_one() already perform.

## References
- https://git.kernel.org/stable/c/2638a9c1521905bb5c5d1e95c8fbc09f79148ed7
- https://git.kernel.org/stable/c/26fe549b5192536b6c1c68a2dfdc8c0dcf9fa4a9
- https://git.kernel.org/stable/c/4fefc6156a162a9f50035c12091a5e5130c82c6e
- https://git.kernel.org/stable/c/60d9c0d6cdde5420d6483c921b16fe5465eb5238
- https://git.kernel.org/stable/c/793385c154771603b8671dd8338927221e9d8d78
- https://git.kernel.org/stable/c/aa308e9dbb9acb17cacdbbce9e4504f69bac8385
- https://git.kernel.org/stable/c/aa8963fdce667a42fb7f0bdd2909fadcab02f9a8
- https://git.kernel.org/stable/c/d16e38fac09a47bfcf98c1ad65a1bb53f94540f5
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46322.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46322
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
