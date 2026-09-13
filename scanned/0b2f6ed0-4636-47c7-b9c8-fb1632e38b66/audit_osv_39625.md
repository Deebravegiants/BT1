# [H] tap: free page on error paths in tap_get_user_xdp()

## Summary
Severity: High
Advisory: CVE-2026-46320
Ecosystem: Linux
CVSS: 7.4 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-06-09
Source: https://osv.dev/vulnerability/CVE-2026-46320
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.94, >=6.13.0 <6.18.36, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

tap: free page on error paths in tap_get_user_xdp()

tap_get_user_xdp() rejects a frame shorter than ETH_HLEN with -EINVAL,
and returns -ENOMEM when build_skb() fails. Both paths jump to the err
label without freeing the page that vhost_net_build_xdp() allocated for
the frame. tap_sendmsg() discards the per-buffer return value and always
returns 0, so vhost_tx_batch() takes the success path and never frees
the page; each rejected frame in a batch leaks one page-frag chunk.

Free the page on both error paths, before the skb is built. This is the
tap counterpart of the same leak in tun_xdp_one().

## References
- https://git.kernel.org/stable/c/18a84c35842e19cd3c5534d8cee73d31863f696d
- https://git.kernel.org/stable/c/3bcf7aec6a9d16438f2cec29f5d7c8d5b8edf9b2
- https://git.kernel.org/stable/c/3f52a86a482a69294c50a5a2a097bd6f4104990a
- https://git.kernel.org/stable/c/8d03e65eb6cfbffec471a6b65416f93679bf3286
- https://git.kernel.org/stable/c/d30aac0fa00ca0afc3e08174cf7f974a66bdcf05
- https://git.kernel.org/stable/c/d68eab61944a9b0826fa2e954e42db1aa3201b7a
- https://git.kernel.org/stable/c/e27c17346628cb56843a83f93ac63c314c00f388
- https://git.kernel.org/stable/c/f979971835dddbca86cf99e3b2e2b94a408a1ab2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46320.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46320
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
