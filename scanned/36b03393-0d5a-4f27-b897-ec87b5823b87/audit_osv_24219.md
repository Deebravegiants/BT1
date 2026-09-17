# [H] drm/nouveau: fix a use-after-free in nouveau_gem_prime_import_sg_table()

## Summary
Severity: High
Advisory: CVE-2022-50454
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-01
Source: https://osv.dev/vulnerability/CVE-2022-50454
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.4.220, >=5.5.0 <5.10.150, >=5.11.0 <5.15.75, >=5.16.0 <5.19.17, >=5.20.0 <6.0.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/nouveau: fix a use-after-free in nouveau_gem_prime_import_sg_table()

nouveau_bo_init() is backed by ttm_bo_init() and ferries its return code
back to the caller. On failures, ttm will call nouveau_bo_del_ttm() and
free the memory.Thus, when nouveau_bo_init() returns an error, the gem
object has already been released. Then the call to nouveau_bo_ref() will
use the freed "nvbo->bo" and lead to a use-after-free bug.

We should delete the call to nouveau_bo_ref() to avoid the use-after-free.

## References
- https://git.kernel.org/stable/c/3aeda2fe6517cc52663d4ce3588dd43f0d4124a7
- https://git.kernel.org/stable/c/540dfd188ea2940582841c1c220bd035a7db0e51
- https://git.kernel.org/stable/c/56ee9577915dc06f55309901012a9ef68dbdb5a8
- https://git.kernel.org/stable/c/5d6093c49c098d86c7b136aba9922df44aeb6944
- https://git.kernel.org/stable/c/7d80473e9f12548ac05b36af4fb9ce80f2f73509
- https://git.kernel.org/stable/c/861f085f81fd569b02cc2c11165a9e6cca144424
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50454.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50454
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
