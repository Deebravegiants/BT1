# [M] CVE-2017-6850

## Summary
Severity: Medium
Advisory: CVE-2017-6850
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/CVE-2017-6850
Type: osv

## Details
The jp2_cdef_destroy function in jp2_cod.c in JasPer before 2.0.13 allows remote attackers to cause a denial of service (NULL pointer dereference) via a crafted image.

## References
- https://usn.ubuntu.com/3693-1/
- https://blogs.gentoo.org/ago/2017/01/25/jasper-null-pointer-dereference-in-jp2_cdef_destroy-jp2_cod-c/
- https://github.com/mdadams/jasper/commit/e96fc4fdd525fa0ede28074a7e2b1caf94b58b0d
- https://github.com/mdadams/jasper/issues/112
