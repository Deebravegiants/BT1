# [H] drm/panfrost: Fix GEM handle creation ref-counting

## Summary
Severity: High
Advisory: CVE-2022-50417
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2022-50417
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.2.0 <5.10.163, >=5.11.0 <5.15.87, >=5.16.0 <6.0.19, >=6.1.0 <6.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/panfrost: Fix GEM handle creation ref-counting

panfrost_gem_create_with_handle() previously returned a BO but with the
only reference being from the handle, which user space could in theory
guess and release, causing a use-after-free. Additionally if the call to
panfrost_gem_mapping_get() in panfrost_ioctl_create_bo() failed then
a(nother) reference on the BO was dropped.

The _create_with_handle() is a problematic pattern, so ditch it and
instead create the handle in panfrost_ioctl_create_bo(). If the call to
panfrost_gem_mapping_get() fails then this means that user space has
indeed gone behind our back and freed the handle. In which case just
return an error code.

## References
- https://git.kernel.org/stable/c/0b70f6ea4d4f2b4d4b291d86ab76b4d07394932c
- https://git.kernel.org/stable/c/3f9feffa8a5ab08b4e298a27b1aa7204a7d42ca2
- https://git.kernel.org/stable/c/4217c6ac817451d5116687f3cc6286220dc43d49
- https://git.kernel.org/stable/c/4f1105ee72d8c7c35d90e3491b31b2d9d6b7e33a
- https://git.kernel.org/stable/c/ba3d2c2380e7129b525a787489c0b7e819a3b898
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50417.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50417
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
