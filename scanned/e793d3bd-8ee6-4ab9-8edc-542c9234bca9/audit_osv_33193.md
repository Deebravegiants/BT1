# [H] can: xilinx_can: xcan_write_frame(): fix use-after-free of transmitted SKB

## Summary
Severity: High
Advisory: CVE-2025-39873
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-23
Source: https://osv.dev/vulnerability/CVE-2025-39873
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <5.15.194, >=5.16.0 <6.1.153, >=6.2.0 <6.6.107, >=6.7.0 <6.12.48, >=6.13.0 <6.16.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: xilinx_can: xcan_write_frame(): fix use-after-free of transmitted SKB

can_put_echo_skb() takes ownership of the SKB and it may be freed
during or after the call.

However, xilinx_can xcan_write_frame() keeps using SKB after the call.

Fix that by only calling can_put_echo_skb() after the code is done
touching the SKB.

The tx_lock is held for the entire xcan_write_frame() execution and
also on the can_get_echo_skb() side so the order of operations does not
matter.

An earlier fix commit 3d3c817c3a40 ("can: xilinx_can: Fix usage of skb
memory") did not move the can_put_echo_skb() call far enough.

[mkl: add "commit" in front of sha1 in patch description]
[mkl: fix indention]

## References
- https://git.kernel.org/stable/c/1139321161a3ba5e45e61e0738b37f42f20bc57a
- https://git.kernel.org/stable/c/668cc1e3bb21101d074e430de1b7ba8fd10189e7
- https://git.kernel.org/stable/c/725b33deebd6e4c96fe7893f384510a54258f28f
- https://git.kernel.org/stable/c/94b050726288a56a6b8ff55aa641f2fedbd3b44c
- https://git.kernel.org/stable/c/e202ffd9e54538ef67ec301ebd6d9da4823466c9
- https://git.kernel.org/stable/c/ef79f00be72bd81d2e1e6f060d83cf7e425deee4
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39873.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39873
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
