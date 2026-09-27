# [C] CVE-2023-25139

## Summary
Severity: Critical
Advisory: CVE-2023-25139
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-02-03
Source: https://osv.dev/vulnerability/CVE-2023-25139
Type: osv

## Details
sprintf in the GNU C Library (glibc) 2.37 has a buffer overflow (out-of-bounds write) in some situations with a correct buffer size. This is unrelated to CWE-676. It may write beyond the bounds of the destination buffer when attempting to write a padded, thousands-separated string representation of a number, if the buffer is allocated the exact size required to represent that number as a string. For example, 1,234,567 (with padding to 13) overflows by two bytes.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/25xxx/CVE-2023-25139.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-25139
- https://security.netapp.com/advisory/ntap-20230302-0010/
- https://sourceware.org/bugzilla/show_bug.cgi?id=30068
- http://www.openwall.com/lists/oss-security/2023/02/10/1
