# [H] uio: Fix use-after-free in uio_open

## Summary
Severity: High
Advisory: CVE-2023-52439
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-02-20
Source: https://osv.dev/vulnerability/CVE-2023-52439
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.18.0 <4.19.306, >=4.20.0 <5.4.268, >=5.5.0 <5.10.209, >=5.11.0 <5.15.148, >=5.16.0 <6.1.74, >=6.2.0 <6.6.13, >=6.7.0 <6.7.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

uio: Fix use-after-free in uio_open

core-1				core-2
-------------------------------------------------------
uio_unregister_device		uio_open
				idev = idr_find()
device_unregister(&idev->dev)
put_device(&idev->dev)
uio_device_release
				get_device(&idev->dev)
kfree(idev)
uio_free_minor(minor)
				uio_release
				put_device(&idev->dev)
				kfree(idev)
-------------------------------------------------------

In the core-1 uio_unregister_device(), the device_unregister will kfree
idev when the idev->dev kobject ref is 1. But after core-1
device_unregister, put_device and before doing kfree, the core-2 may
get_device. Then:
1. After core-1 kfree idev, the core-2 will do use-after-free for idev.
2. When core-2 do uio_release and put_device, the idev will be double
   freed.

To address this issue, we can get idev atomic & inc idev reference with
minor_lock.

## References
- https://git.kernel.org/stable/c/0c9ae0b8605078eafc3bea053cc78791e97ba2e2
- https://git.kernel.org/stable/c/17a8519cb359c3b483fb5c7367efa9a8a508bdea
- https://git.kernel.org/stable/c/3174e0f7de1ba392dc191625da83df02d695b60c
- https://git.kernel.org/stable/c/35f102607054faafe78d2a6994b18d5d9d6e92ad
- https://git.kernel.org/stable/c/5cf604ee538ed0c467abe3b4cda5308a6398f0f7
- https://git.kernel.org/stable/c/5e0be1229ae199ebb90b33102f74a0f22d152570
- https://git.kernel.org/stable/c/913205930da6213305616ac539447702eaa85e41
- https://git.kernel.org/stable/c/e93da893d52d82d57fc0db2ca566024e0f26ff50
- https://lists.debian.org/debian-lts-announce/2024/06/msg00016.html
- https://lists.debian.org/debian-lts-announce/2024/06/msg00020.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52439.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52439
- https://security.netapp.com/advisory/ntap-20241227-0006/
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
