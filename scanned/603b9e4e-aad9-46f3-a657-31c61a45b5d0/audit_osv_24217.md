# [H] drm/vmwgfx: Validate the box size for the snooped cursor

## Summary
Severity: High
Advisory: CVE-2022-50440
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2022-50440
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.2.0 <4.9.337, >=4.10.0 <4.14.303, >=4.15.0 <4.19.270, >=4.20.0 <5.4.229, >=5.5.0 <5.10.163, >=5.11.0 <5.15.87, >=5.16.0 <6.0.18, >=6.1.0 <6.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/vmwgfx: Validate the box size for the snooped cursor

Invalid userspace dma surface copies could potentially overflow
the memcpy from the surface to the snooped image leading to crashes.
To fix it the dimensions of the copybox have to be validated
against the expected size of the snooped cursor.

## References
- https://git.kernel.org/stable/c/439cbbc1519547f9a7b483f0de33b556ebfec901
- https://git.kernel.org/stable/c/4cf949c7fafe21e085a4ee386bb2dade9067316e
- https://git.kernel.org/stable/c/4d54d11b49860686331c58a00f733b16a93edfc4
- https://git.kernel.org/stable/c/50d177f90b63ea4138560e500d92be5e4c928186
- https://git.kernel.org/stable/c/622d527decaac0eb65512acada935a0fdc1d0202
- https://git.kernel.org/stable/c/6948e570f54f2044dd4da444b10471373a047eeb
- https://git.kernel.org/stable/c/6b4e70a428b5a11f56db94047b68e144529fe512
- https://git.kernel.org/stable/c/94b283341f9f3f0ed56a360533766377a01540e0
- https://git.kernel.org/stable/c/ee8d31836cbe7c26e207bfa0a4a726f0a25cfcf6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50440.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50440
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
