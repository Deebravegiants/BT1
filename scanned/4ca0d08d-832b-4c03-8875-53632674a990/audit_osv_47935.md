# [M] CVE-2017-15128

## Summary
Severity: Medium
Advisory: CVE-2017-15128
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-01-14
Source: https://osv.dev/vulnerability/CVE-2017-15128
Type: osv

## Details
A flaw was found in the hugetlb_mcopy_atomic_pte function in mm/hugetlb.c in the Linux kernel before 4.13.12. A lack of size check could cause a denial of service (BUG).

## References
- https://access.redhat.com/security/cve/CVE-2017-15128
- https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.13.12
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=1e3921471354244f70fe268586ff94a97a6dd4df
- https://bugzilla.redhat.com/show_bug.cgi?id=1525222
- https://github.com/torvalds/linux/commit/1e3921471354244f70fe268586ff94a97a6dd4df
