# [M] CVE-2021-3470

## Summary
Severity: Medium
Advisory: CVE-2021-3470
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2021-03-31
Source: https://osv.dev/vulnerability/CVE-2021-3470
Type: osv

## Details
A heap overflow issue was found in Redis in versions before 5.0.10, before 6.0.9 and before 6.2.0 when using a heap allocator other than jemalloc or glibc's malloc, leading to potential out of bound write or process crash. Effectively this flaw does not affect the vast majority of users, who use jemalloc or glibc malloc.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1943623
