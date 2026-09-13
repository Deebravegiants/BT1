# [H] CVE-2018-5735

## Summary
Severity: High
Advisory: CVE-2018-5735
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-10-30
Source: https://osv.dev/vulnerability/CVE-2018-5735
Type: osv

## Details
The Debian backport of the fix for CVE-2017-3137 leads to assertion failure in validator.c:1858; Affects Debian versions 9.9.5.dfsg-9+deb8u15; 9.9.5.dfsg-9+deb8u18; 9.10.3.dfsg.P4-12.3+deb9u5; 9.11.5.P4+dfsg-5.1 No ISC releases are affected. Other packages from other distributions who did similar backports for the fix for 2017-3137 may also be affected.

## References
- https://security-tracker.debian.org/tracker/CVE-2018-5735
