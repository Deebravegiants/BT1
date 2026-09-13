# [H] CVE-2018-13843

## Summary
Severity: High
Advisory: CVE-2018-13843
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-07-10
Source: https://osv.dev/vulnerability/CVE-2018-13843
Type: osv

## Details
An issue has been found in HTSlib 1.8. It is a memory leak in bgzf_getline in bgzf.c. NOTE: the software maintainer's position is that the "failure to free memory" can be fixed in applications that use the HTSlib library (such as test/test_bgzf.c in the original report) and is not a library issue

## References
- https://github.com/samtools/htslib/issues/731#issue-339662537
