# [H] net: dlink: handle copy_thresh allocation failure

## Summary
Severity: High
Advisory: CVE-2025-40053
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-10-28
Source: https://osv.dev/vulnerability/CVE-2025-40053
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <5.10.246, >=5.11.0 <5.15.195, >=5.16.0 <6.1.156, >=6.2.0 <6.6.112, >=6.7.0 <6.12.53, >=6.13.0 <6.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: dlink: handle copy_thresh allocation failure

The driver did not handle failure of `netdev_alloc_skb_ip_align()`.
If the allocation failed, dereferencing `skb->protocol` could lead to
a NULL pointer dereference.

This patch tries to allocate `skb`. If the allocation fails, it falls
back to the normal path.

Tested-on: D-Link DGE-550T Rev-A3

## References
- https://git.kernel.org/stable/c/5aa9b885602811a026a3f45c92ea2b4b04c54f09
- https://git.kernel.org/stable/c/7ed5010fef0930f4322d620052edc854ef3ec41f
- https://git.kernel.org/stable/c/8169a6011c5fecc6cb1c3654c541c567d3318de8
- https://git.kernel.org/stable/c/84fd710a704f3d53d4120e452e86cea558cf73a8
- https://git.kernel.org/stable/c/9d49e4b14609e1a20d931e718962c4b6b5485174
- https://git.kernel.org/stable/c/ea87151df398d407a632c7bf63013290f01c5009
- https://git.kernel.org/stable/c/fd7b6b2c920d7fd370a612be416a904d6e1ebe55
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/40xxx/CVE-2025-40053.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-40053
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
