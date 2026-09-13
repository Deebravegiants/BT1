# [H] CVE-2017-18285

## Summary
Severity: High
Advisory: CVE-2017-18285
CVSS: 7.1 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2018-06-04
Source: https://osv.dev/vulnerability/CVE-2017-18285
Type: osv

## Details
The Gentoo app-backup/burp package before 2.1.32 has incorrect group ownership of the /etc/burp directory, which might allow local users to obtain read and write access to arbitrary files by leveraging access to a certain account for a burp-server.conf change.

## References
- https://security.gentoo.org/glsa/201806-03
- https://security.gentoo.org/glsa/201904-05
- https://bugs.gentoo.org/641842
