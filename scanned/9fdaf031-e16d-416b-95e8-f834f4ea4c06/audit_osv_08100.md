# [H] CVE-2016-10250

## Summary
Severity: High
Advisory: CVE-2016-10250
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-15
Source: https://osv.dev/vulnerability/CVE-2016-10250
Type: osv

## Details
The jp2_colr_destroy function in jp2_cod.c in JasPer before 1.900.13 allows remote attackers to cause a denial of service (NULL pointer dereference) by leveraging incorrect cleanup of JP2 box data on error. NOTE: this vulnerability exists because of an incomplete fix for CVE-2016-8887.

## References
- https://usn.ubuntu.com/3693-1/
- https://blogs.gentoo.org/ago/2016/10/23/jasper-null-pointer-dereference-in-jp2_colr_destroy-jp2_cod-c-incomplete-fix-for-cve-2016-8887/
- https://github.com/mdadams/jasper/commit/bdfe95a6e81ffb4b2fad31a76b57943695beed20
