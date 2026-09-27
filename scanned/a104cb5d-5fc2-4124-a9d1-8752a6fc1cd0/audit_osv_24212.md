# [H] rpmsg: char: Avoid double destroy of default endpoint

## Summary
Severity: High
Advisory: CVE-2022-50421
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2022-50421
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <5.19.17, >=5.20.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

rpmsg: char: Avoid double destroy of default endpoint

The rpmsg_dev_remove() in rpmsg_core is the place for releasing
this default endpoint.

So need to avoid destroying the default endpoint in
rpmsg_chrdev_eptdev_destroy(), this should be the same as
rpmsg_eptdev_release(). Otherwise there will be double destroy
issue that ept->refcount report warning:

refcount_t: underflow; use-after-free.

Call trace:
 refcount_warn_saturate+0xf8/0x150
 virtio_rpmsg_destroy_ept+0xd4/0xec
 rpmsg_dev_remove+0x60/0x70

The issue can be reproduced by stopping remoteproc before
closing the /dev/rpmsgX.

## References
- https://git.kernel.org/stable/c/3f20ef7a845c2c8d7ec82ecffa20d95cab5ecfeb
- https://git.kernel.org/stable/c/467233a4ac29b215d492843d067a9f091e6bf0c5
- https://git.kernel.org/stable/c/ef828a39d6a7028836eaf37df3ad568c8c2dd6f9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50421.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50421
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
