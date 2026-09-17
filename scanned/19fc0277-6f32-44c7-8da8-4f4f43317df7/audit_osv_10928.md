# [H] CVE-2017-5180

## Summary
Severity: High
Advisory: CVE-2017-5180
CVSS: 8.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-02-09
Source: https://osv.dev/vulnerability/CVE-2017-5180
Type: osv

## Details
Firejail before 0.9.44.4 and 0.9.38.x LTS before 0.9.38.8 LTS does not consider the .Xauthority case during its attempt to prevent accessing user files with an euid of zero, which allows local users to conduct sandbox-escape attacks via vectors involving a symlink and the --private option.

## References
- http://openwall.com/lists/oss-security/2017/01/04/2
- http://www.securityfocus.com/bid/95298
- https://firejail.wordpress.com/download-2/release-notes/
- https://security.gentoo.org/glsa/201701-62
