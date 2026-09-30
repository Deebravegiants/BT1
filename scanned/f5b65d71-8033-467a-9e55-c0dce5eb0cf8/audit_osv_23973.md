# [H] usb: gadget: f_fs: Prevent race during ffs_ep0_queue_wait

## Summary
Severity: High
Advisory: CVE-2022-49755
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2022-49755
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.35 <4.14.305, >=4.15.0 <4.19.272, >=4.20.0 <5.4.231, >=5.5.0 <5.10.166, >=5.11.0 <5.15.91, >=5.16.0 <6.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

usb: gadget: f_fs: Prevent race during ffs_ep0_queue_wait

While performing fast composition switch, there is a possibility that the
process of ffs_ep0_write/ffs_ep0_read get into a race condition
due to ep0req being freed up from functionfs_unbind.

Consider the scenario that the ffs_ep0_write calls the ffs_ep0_queue_wait
by taking a lock &ffs->ev.waitq.lock. However, the functionfs_unbind isn't
bounded so it can go ahead and mark the ep0req to NULL, and since there
is no NULL check in ffs_ep0_queue_wait we will end up in use-after-free.

Fix this by making a serialized execution between the two functions using
a mutex_lock(ffs->mutex).

## References
- https://git.kernel.org/stable/c/6a19da111057f69214b97c62fb0ac59023970850
- https://git.kernel.org/stable/c/6aee197b7fbcd61596a78b47d553f2f99111f217
- https://git.kernel.org/stable/c/6dd9ea05534f323668db94fcc2726c7a84547e78
- https://git.kernel.org/stable/c/a8d40942df074f4ebcb9bd3413596d92f323b064
- https://git.kernel.org/stable/c/ae8e136bcaae96163b5821984de1036efc9abb1a
- https://git.kernel.org/stable/c/e9036e951f93fb8d7b5e9d6e2c7f94a4da312ae4
- https://git.kernel.org/stable/c/facf353c9e8d7885b686d9a4b173d4e0af6441d2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49755.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49755
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
