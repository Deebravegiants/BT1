# [H] CVE-2018-11803

## Summary
Severity: High
Advisory: CVE-2018-11803
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-02-05
Source: https://osv.dev/vulnerability/CVE-2018-11803
Type: osv

## Details
Subversion's mod_dav_svn Apache HTTPD module versions 1.11.0 and 1.10.0 to 1.10.3 will crash after dereferencing an uninitialized pointer if the client omits the root path in a recursive directory listing operation.

## References
- https://lists.apache.org/thread.html/fa71074862373c142d264534385f8ea5d8d6b80d27f36f3c46f55003%40%3Cdev.subversion.apache.org%3E
- http://www.securityfocus.com/bid/106770
- https://security.gentoo.org/glsa/201904-08
- https://usn.ubuntu.com/3869-1/
