# [M] drm/amdkfd: Fix NULL pointer dereference in svm_migrate_to_ram()

## Summary
Severity: Medium
Advisory: CVE-2022-49864
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-05-01
Source: https://osv.dev/vulnerability/CVE-2022-49864
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.79, >=5.16.0 <6.0.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdkfd: Fix NULL pointer dereference in svm_migrate_to_ram()

./drivers/gpu/drm/amd/amdkfd/kfd_migrate.c:985:58-62: ERROR: p is NULL but dereferenced.

## References
- https://git.kernel.org/stable/c/3c1bb6187e566143f15dbf0367ae671584aead5b
- https://git.kernel.org/stable/c/5b994354af3cab770bf13386469c5725713679af
- https://git.kernel.org/stable/c/613d5a9a440828970f1543b962779401ac2c9c62
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49864.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49864
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
