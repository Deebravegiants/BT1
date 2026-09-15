# [M] CVE-2019-14871

## Summary
Severity: Medium
Advisory: CVE-2019-14871
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-03-18
Source: https://osv.dev/vulnerability/CVE-2019-14871
Type: osv

## Details
The REENT_CHECK macro (see newlib/libc/include/sys/reent.h) as used by REENT_CHECK_TM, REENT_CHECK_MISC, REENT_CHECK_MP and other newlib macros in versions prior to 3.3.0, does not check for memory allocation problems when the DEBUG flag is unset (as is the case in production firmware builds).

## References
- https://census-labs.com/news/2020/01/31/multiple-null-pointer-dereference-vulnerabilities-in-newlib/
