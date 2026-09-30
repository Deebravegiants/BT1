# [M] integrity: Fix memory leakage in keyring allocation error path

## Summary
Severity: Medium
Advisory: CVE-2022-50395
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2022-50395
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.12.0 <5.4.229, >=5.5.0 <5.10.163, >=5.11.0 <5.15.86, >=5.16.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

integrity: Fix memory leakage in keyring allocation error path

Key restriction is allocated in integrity_init_keyring(). However, if
keyring allocation failed, it is not freed, causing memory leaks.

## References
- https://git.kernel.org/stable/c/29d6c69ba4b96a1de0376e44e5f8b38b13ec8803
- https://git.kernel.org/stable/c/39419ef7af0916cc3620ecf1ed42d29659109bf3
- https://git.kernel.org/stable/c/3bd737289c26be3cee4b9afaf61ef784a2af9d6e
- https://git.kernel.org/stable/c/57e49ad12f8f5df0c48e1710c54b147a05a10c32
- https://git.kernel.org/stable/c/9b7c44885a07c5ee7f9bf3aa3c9c72fb110c8d22
- https://git.kernel.org/stable/c/c591c48842f08d30ec6b8416757831985ed9a315
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50395.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50395
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
