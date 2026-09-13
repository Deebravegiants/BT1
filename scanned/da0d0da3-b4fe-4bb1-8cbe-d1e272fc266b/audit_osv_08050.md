# [M] CVE-2016-10130

## Summary
Severity: Medium
Advisory: CVE-2016-10130
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-03-24
Source: https://osv.dev/vulnerability/CVE-2016-10130
Type: osv

## Details
The http_connect function in transports/http.c in libgit2 before 0.24.6 and 0.25.x before 0.25.1 might allow man-in-the-middle attackers to spoof servers by leveraging clobbering of the error variable.

## References
- http://www.securityfocus.com/bid/95359
- http://lists.opensuse.org/opensuse-updates/2017-02/msg00030.html
- http://lists.opensuse.org/opensuse-updates/2017-02/msg00036.html
- http://lists.opensuse.org/opensuse-updates/2017-02/msg00072.html
- http://www.openwall.com/lists/oss-security/2017/01/10/5
- http://www.openwall.com/lists/oss-security/2017/01/11/6
- https://github.com/libgit2/libgit2/commit/9a64e62f0f20c9cf9b2e1609f037060eb2d8eb22
- https://github.com/libgit2/libgit2/commit/b5c6a1b407b7f8b952bded2789593b68b1876211
- https://libgit2.github.com/security/
