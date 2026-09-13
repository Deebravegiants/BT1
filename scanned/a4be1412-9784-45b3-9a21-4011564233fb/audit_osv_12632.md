# [H] CVE-2018-13844

## Summary
Severity: High
Advisory: CVE-2018-13844
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-07-10
Source: https://osv.dev/vulnerability/CVE-2018-13844
Type: osv

## Details
An issue has been found in HTSlib 1.8. It is a memory leak in fai_read in faidx.c. NOTE: This has been disputed with the assertion that this vulnerability exists in the test harness and HTSlib users would be aware of the need to destruct this object returned by fai_load() in their own code

## References
- https://github.com/samtools/htslib/issues/731#issuecomment-403675330
