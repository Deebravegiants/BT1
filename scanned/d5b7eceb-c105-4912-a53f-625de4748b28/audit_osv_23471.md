# [H] drm/virtio: Fix GEM handle creation UAF

## Summary
Severity: High
Advisory: CVE-2022-48899
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-21
Source: https://osv.dev/vulnerability/CVE-2022-48899
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.4.0 <4.19.270, >=4.20.0 <5.4.229, >=5.5.0 <5.10.164, >=5.11.0 <5.15.89, >=5.16.0 <6.1.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/virtio: Fix GEM handle creation UAF

Userspace can guess the handle value and try to race GEM object creation
with handle close, resulting in a use-after-free if we dereference the
object after dropping the handle's reference.  For that reason, dropping
the handle's reference must be done *after* we are done dereferencing
the object.

## References
- https://git.kernel.org/stable/c/011ecdbcd520c90c344b872ca6b4821f7783b2f8
- https://git.kernel.org/stable/c/19ec87d06acfab2313ee82b2a689bf0c154e57ea
- https://git.kernel.org/stable/c/52531258318ed59a2dc5a43df2eaf0eb1d65438e
- https://git.kernel.org/stable/c/68bcd063857075d2f9edfed6024387ac377923e2
- https://git.kernel.org/stable/c/adc48e5e408afbb01d261bd303fd9fbbbaa3e317
- https://git.kernel.org/stable/c/d01d6d2b06c0d8390adf8f3ba08aa60b5642ef73
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/48xxx/CVE-2022-48899.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-48899
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
