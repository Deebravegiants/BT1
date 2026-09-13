# [M] CVE-2022-3104

## Summary
Severity: Medium
Advisory: CVE-2022-3104
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-12-14
Source: https://osv.dev/vulnerability/CVE-2022-3104
Type: osv

## Details
An issue was discovered in the Linux kernel through 5.16-rc6. lkdtm_ARRAY_BOUNDS in drivers/misc/lkdtm/bugs.c lacks check of the return value of kmalloc() and will cause the null pointer dereference.

## References
- https://git.kernel.org/pub/scm/linux/kernel/git/torvalds/linux.git/commit/?h=v5.19-rc2&id=4a9800c81d2f34afb66b4b42e0330ae8298019a2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/3xxx/CVE-2022-3104.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-3104
- https://bugzilla.redhat.com/show_bug.cgi?id=2153062
