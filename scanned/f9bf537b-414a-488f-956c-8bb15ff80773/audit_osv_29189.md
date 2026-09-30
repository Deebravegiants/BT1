# [H] ax25: Fix refcount imbalance on inbound connections

## Summary
Severity: High
Advisory: CVE-2024-40910
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-12
Source: https://osv.dev/vulnerability/CVE-2024-40910
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.95, >=6.2.0 <6.6.35, >=6.7.0 <6.9.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

ax25: Fix refcount imbalance on inbound connections

When releasing a socket in ax25_release(), we call netdev_put() to
decrease the refcount on the associated ax.25 device. However, the
execution path for accepting an incoming connection never calls
netdev_hold(). This imbalance leads to refcount errors, and ultimately
to kernel crashes.

A typical call trace for the above situation will start with one of the
following errors:

    refcount_t: decrement hit 0; leaking memory.
    refcount_t: underflow; use-after-free.

And will then have a trace like:

    Call Trace:
    <TASK>
    ? show_regs+0x64/0x70
    ? __warn+0x83/0x120
    ? refcount_warn_saturate+0xb2/0x100
    ? report_bug+0x158/0x190
    ? prb_read_valid+0x20/0x30
    ? handle_bug+0x3e/0x70
    ? exc_invalid_op+0x1c/0x70
    ? asm_exc_invalid_op+0x1f/0x30
    ? refcount_warn_saturate+0xb2/0x100
    ? refcount_warn_saturate+0xb2/0x100
    ax25_release+0x2ad/0x360
    __sock_release+0x35/0xa0
    sock_close+0x19/0x20
    [...]

On reboot (or any attempt to remove the interface), the kernel gets
stuck in an infinite loop:

    unregister_netdevice: waiting for ax0 to become free. Usage count = 0

This patch corrects these issues by ensuring that we call netdev_hold()
and ax25_dev_hold() for new connections in ax25_accept(). This makes the
logic leading to ax25_accept() match the logic for ax25_bind(): in both
cases we increment the refcount, which is ultimately decremented in
ax25_release().

## References
- https://git.kernel.org/stable/c/3c34fb0bd4a4237592c5ecb5b2e2531900c55774
- https://git.kernel.org/stable/c/52100fd74ad07b53a4666feafff1cd11436362d3
- https://git.kernel.org/stable/c/a723a6c8d4831cc8e2c7b0c9f3f0c010d4671964
- https://git.kernel.org/stable/c/f4df9d6c8d4e4c818252b0419c2165d66eabd4eb
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/40xxx/CVE-2024-40910.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-40910
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
