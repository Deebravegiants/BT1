# [M] CVE-2018-15746

## Summary
Severity: Medium
Advisory: CVE-2018-15746
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-08-29
Source: https://osv.dev/vulnerability/CVE-2018-15746
Type: osv

## Details
qemu-seccomp.c in QEMU might allow local OS guest users to cause a denial of service (guest crash) by leveraging mishandling of the seccomp policy for threads other than the main thread.

## References
- http://www.openwall.com/lists/oss-security/2018/08/28/6
- https://access.redhat.com/errata/RHSA-2019:2425
- https://lists.gnu.org/archive/html/qemu-devel/2018-08/msg04892.html
