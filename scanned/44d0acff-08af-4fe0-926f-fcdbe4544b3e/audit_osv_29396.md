# [H] net/iucv: fix use after free in iucv_sock_close()

## Summary
Severity: High
Advisory: CVE-2024-42271
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-17
Source: https://osv.dev/vulnerability/CVE-2024-42271
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.4.0 <4.19.320, >=4.20.0 <5.4.282, >=5.5.0 <5.10.224, >=5.11.0 <5.15.165, >=5.16.0 <6.1.104, >=6.2.0 <6.6.45, >=6.7.0 <6.10.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/iucv: fix use after free in iucv_sock_close()

iucv_sever_path() is called from process context and from bh context.
iucv->path is used as indicator whether somebody else is taking care of
severing the path (or it is already removed / never existed).
This needs to be done with atomic compare and swap, otherwise there is a
small window where iucv_sock_close() will try to work with a path that has
already been severed and freed by iucv_callback_connrej() called by
iucv_tasklet_fn().

Example:
[452744.123844] Call Trace:
[452744.123845] ([<0000001e87f03880>] 0x1e87f03880)
[452744.123966]  [<00000000d593001e>] iucv_path_sever+0x96/0x138
[452744.124330]  [<000003ff801ddbca>] iucv_sever_path+0xc2/0xd0 [af_iucv]
[452744.124336]  [<000003ff801e01b6>] iucv_sock_close+0xa6/0x310 [af_iucv]
[452744.124341]  [<000003ff801e08cc>] iucv_sock_release+0x3c/0xd0 [af_iucv]
[452744.124345]  [<00000000d574794e>] __sock_release+0x5e/0xe8
[452744.124815]  [<00000000d5747a0c>] sock_close+0x34/0x48
[452744.124820]  [<00000000d5421642>] __fput+0xba/0x268
[452744.124826]  [<00000000d51b382c>] task_work_run+0xbc/0xf0
[452744.124832]  [<00000000d5145710>] do_notify_resume+0x88/0x90
[452744.124841]  [<00000000d5978096>] system_call+0xe2/0x2c8
[452744.125319] Last Breaking-Event-Address:
[452744.125321]  [<00000000d5930018>] iucv_path_sever+0x90/0x138
[452744.125324]
[452744.125325] Kernel panic - not syncing: Fatal exception in interrupt

Note that bh_lock_sock() is not serializing the tasklet context against
process context, because the check for sock_owned_by_user() and
corresponding handling is missing.

Ideas for a future clean-up patch:
A) Correct usage of bh_lock_sock() in tasklet context, as described in
Re-enqueue, if needed. This may require adding return values to the
tasklet functions and thus changes to all users of iucv.

B) Change iucv tasklet into worker and use only lock_sock() in af_iucv.

## References
- https://git.kernel.org/stable/c/01437282fd3904810603f3dc98d2cac6b8b6fc84
- https://git.kernel.org/stable/c/37652fbef9809411cea55ea5fa1a170e299efcd0
- https://git.kernel.org/stable/c/69620522c48ce8215e5eb55ffbab8cafee8f407d
- https://git.kernel.org/stable/c/84f40b46787ecb67c7ad08a5bb1376141fa10c01
- https://git.kernel.org/stable/c/8b424c9e44111c5a76f41c6b741f8d4c4179d876
- https://git.kernel.org/stable/c/ac758e1f663fe9bc64f6b47212a2aa18697524f5
- https://git.kernel.org/stable/c/c65f72eec60a34ace031426e04e9aff8e5f04895
- https://git.kernel.org/stable/c/f558120cd709682b739207b48cf7479fd9568431
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42271.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42271
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
