# [H] vsock/virtio: fix zerocopy completion for multi-skb sends

## Summary
Severity: High
Advisory: CVE-2026-53365
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-13
Source: https://osv.dev/vulnerability/CVE-2026-53365
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.12.97, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

vsock/virtio: fix zerocopy completion for multi-skb sends

When a large message is fragmented into multiple skbs, the zerocopy
uarg is only allocated and attached to the last skb in the loop.
Non-final skbs carry pinned user pages with no completion tracking,
so the kernel has no way to notify userspace when those pages are safe
to reuse. If the loop breaks early the uarg is never allocated at all,
leaking pinned pages with no completion notification.

Fix this by following the approach used by TCP: allocate the zerocopy
uarg (if not provided by the caller) before the send loop and attach
it to every skb via skb_zcopy_set(), which takes a reference per skb.
Each skb's completion properly decrements the refcount, and the
notification only fires after the last skb is freed.
On failure, if no data was sent, the uarg is cleanly aborted via
net_zcopy_put_abort().

This issue was initially discovered by sashiko while reviewing commit
1cb36e252211 ("vsock/virtio: fix MSG_ZEROCOPY pinned-pages accounting")
but was pre-existing.

## References
- https://git.kernel.org/stable/c/293fe8f2d1b5ac464ca16a8eba09571bbbb34ba9
- https://git.kernel.org/stable/c/76b995bc57bd90cb6e954e1966fbd8786da47f0d
- https://git.kernel.org/stable/c/ae38d9179190a956e2a87a69ef1dd6f451b51c4d
- https://git.kernel.org/stable/c/b3155f2b78db21e99256bcf7eb902f24ff6d5338
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53365.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53365
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
- https://github.com/MaherAzzouzi/vsockdrop
