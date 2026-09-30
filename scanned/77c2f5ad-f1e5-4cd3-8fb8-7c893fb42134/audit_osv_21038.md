# [H] CVE-2021-3998

## Summary
Severity: High
Advisory: CVE-2021-3998
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2022-08-24
Source: https://osv.dev/vulnerability/CVE-2021-3998
Type: osv

## Details
A flaw was found in glibc. The realpath() function can mistakenly return an unexpected value, potentially leading to information leakage and disclosure of sensitive data.

## References
- https://sourceware.org/git/gitweb.cgi?p=glibc.git%3Bh=84d2d0fe20bdf94feed82b21b4d7d136db471f03
- https://sourceware.org/git/gitweb.cgi?p=glibc.git%3Bh=ee8d5e33adb284601c00c94687bc907e10aec9bb
- https://access.redhat.com/security/cve/CVE-2021-3998
- https://security-tracker.debian.org/tracker/CVE-2021-3998
- https://security.netapp.com/advisory/ntap-20221020-0003/
- https://bugzilla.redhat.com/show_bug.cgi?id=2024633
- https://sourceware.org/bugzilla/show_bug.cgi?id=28770
- https://www.openwall.com/lists/oss-security/2022/01/24/4
