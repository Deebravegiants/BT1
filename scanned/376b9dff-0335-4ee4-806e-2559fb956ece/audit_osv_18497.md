# [H] CVE-2020-28010

## Summary
Severity: High
Advisory: CVE-2020-28010
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-05-06
Source: https://osv.dev/vulnerability/CVE-2020-28010
Type: osv

## Details
Exim 4 before 4.94.2 allows Out-of-bounds Write because the main function, while setuid root, copies the current working directory pathname into a buffer that is too small (on some common platforms).

## References
- http://www.openwall.com/lists/oss-security/2021/07/22/7
- https://www.exim.org/static/doc/security/CVE-2020-qualys/CVE-2020-28010-SLCWD.txt
