# [C] CVE-2016-3067

## Summary
Severity: Critical
Advisory: CVE-2016-3067
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-21
Source: https://osv.dev/vulnerability/CVE-2016-3067
Type: osv

## Details
Cygwin before 2.5.0 does not properly handle updating permissions when changing users, which allows attackers to gain privileges.

## References
- https://sourceware.org/git/?p=newlib-cygwin.git%3Ba=commit%3Bh=205862ed08649df8f50b926a2c58c963f571b044
- https://cygwin.com/ml/cygwin-announce/2016-02/msg00023.html
- https://cygwin.com/ml/cygwin-announce/2016-04/msg00020.html
- https://cygwin.com/ml/cygwin-announce/2016-04/msg00054.html
- https://cygwin.com/ml/cygwin/2016-02/msg00129.html
