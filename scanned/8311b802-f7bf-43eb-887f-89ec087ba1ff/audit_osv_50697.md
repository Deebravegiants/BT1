# [H] CVE-2020-29369

## Summary
Severity: High
Advisory: CVE-2020-29369
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-11-28
Source: https://osv.dev/vulnerability/CVE-2020-29369
Type: osv

## Details
An issue was discovered in mm/mmap.c in the Linux kernel before 5.7.11. There is a race condition between certain expand functions (expand_downwards and expand_upwards) and page-table free operations from an munmap call, aka CID-246c320a8cfe.

## References
- https://cdn.kernel.org/pub/linux/kernel/v5.x/ChangeLog-5.7.11
- https://security.netapp.com/advisory/ntap-20210115-0001/
- http://www.openwall.com/lists/oss-security/2021/02/10/6
- http://www.openwall.com/lists/oss-security/2021/02/19/8
- https://bugs.chromium.org/p/project-zero/issues/detail?id=2056
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?id=246c320a8cfe0b11d81a4af38fa9985ef0cc9a4c
