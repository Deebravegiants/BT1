# [H] CVE-2017-9078

## Summary
Severity: High
Advisory: CVE-2017-9078
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-19
Source: https://osv.dev/vulnerability/CVE-2017-9078
Type: osv

## Details
The server in Dropbear before 2017.75 might allow post-authentication root remote code execution because of a double free in cleanup of TCP listeners when the -a option is enabled.

## References
- http://www.debian.org/security/2017/dsa-3859
- https://security.netapp.com/advisory/ntap-20191004-0006/
- http://lists.ucc.gu.uwa.edu.au/pipermail/dropbear/2017q2/001985.html
