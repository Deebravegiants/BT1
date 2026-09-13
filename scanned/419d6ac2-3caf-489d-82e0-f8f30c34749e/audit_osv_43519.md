# [H] vfio/qat: fix f_pos race in qat_vf_resume_write()

## Summary
Severity: High
Advisory: CVE-2026-74306
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-74306
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

vfio/qat: fix f_pos race in qat_vf_resume_write()

qat_vf_resume_write() checks filp->f_pos before taking migf->lock, but
copies into the migration-state buffer after taking the lock and
re-reading the shared file position.

Two concurrent writers could therefore pass the bounds check with the
old offset, then have the second writer copy after the first advanced
f_pos, writing past the end of the migration-state buffer.

Take migf->lock before doing the boundary checks.

## References
- https://git.kernel.org/stable/c/4ec5e932e636896e97e4c6a8205b0ac76d52421a
- https://git.kernel.org/stable/c/6465af0004dc1b067129a26ef44f19cdf13bbce6
- https://git.kernel.org/stable/c/b6fd7a40a66485c8aa8156d8fcf50b95cb8ba281
- https://git.kernel.org/stable/c/d416dcefdbac90d96b22485fd93f28229ad9984b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74306.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74306
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
