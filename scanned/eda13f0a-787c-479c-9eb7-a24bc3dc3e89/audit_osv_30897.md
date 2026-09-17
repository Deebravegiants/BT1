# [M] ALSA: core: Fix possible NULL dereference caused by kunit_kzalloc()

## Summary
Severity: Medium
Advisory: CVE-2024-56696
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-28
Source: https://osv.dev/vulnerability/CVE-2024-56696
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.9.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ALSA: core: Fix possible NULL dereference caused by kunit_kzalloc()

kunit_kzalloc() may return a NULL pointer, dereferencing it without
NULL check may lead to NULL dereference.
Add NULL checks for all the kunit_kzalloc() in sound_kunit.c

## References
- https://git.kernel.org/stable/c/8bfff486ecc79a72e9380e2d5e0ff234d5542d2f
- https://git.kernel.org/stable/c/9ad467a2b2716d4ed12f003b041aa6c776a13ff5
- https://git.kernel.org/stable/c/f5486bf8abfe778b368d8fd1aa655dc01d0013ca
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56696.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56696
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
