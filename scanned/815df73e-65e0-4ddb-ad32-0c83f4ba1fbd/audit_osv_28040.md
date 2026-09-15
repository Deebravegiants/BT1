# [H] media: edia: dvbdev: fix a use-after-free

## Summary
Severity: High
Advisory: CVE-2024-27043
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-01
Source: https://osv.dev/vulnerability/CVE-2024-27043
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.21 <4.19.311, >=4.20.0 <5.4.273, >=5.5.0 <5.10.214, >=5.11.0 <5.15.153, >=5.16.0 <6.1.83, >=6.2.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: edia: dvbdev: fix a use-after-free

In dvb_register_device, *pdvbdev is set equal to dvbdev, which is freed
in several error-handling paths. However, *pdvbdev is not set to NULL
after dvbdev's deallocation, causing use-after-frees in many places,
for example, in the following call chain:

budget_register
  |-> dvb_dmxdev_init
        |-> dvb_register_device
  |-> dvb_dmxdev_release
        |-> dvb_unregister_device
              |-> dvb_remove_device
                    |-> dvb_device_put
                          |-> kref_put

When calling dvb_unregister_device, dmxdev->dvbdev (i.e. *pdvbdev in
dvb_register_device) could point to memory that had been freed in
dvb_register_device. Thereafter, this pointer is transferred to
kref_put and triggering a use-after-free.

## References
- https://git.kernel.org/stable/c/096237039d00c839f3e3a5fe6d001bf0db45b644
- https://git.kernel.org/stable/c/0d3fe80b6d175c220b3e252efc6c6777e700e98e
- https://git.kernel.org/stable/c/35674111a043b0482a9bc69da8850a83f465b07d
- https://git.kernel.org/stable/c/437a111f79a2f5b2a5f21e27fdec6f40c8768712
- https://git.kernel.org/stable/c/779e8db7efb22316c8581d6c229636d2f5694a62
- https://git.kernel.org/stable/c/8c64f4cdf4e6cc5682c52523713af8c39c94e6d5
- https://git.kernel.org/stable/c/b7586e902128e4fb7bfbb661cb52e4215a65637b
- https://git.kernel.org/stable/c/d0f5c28333822f9baa5280d813124920720fd856
- https://git.kernel.org/stable/c/f20c3270f3ed5aa6919a87e4de9bf6c05fb57086
- https://lists.debian.org/debian-lts-announce/2024/06/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27043.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27043
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
