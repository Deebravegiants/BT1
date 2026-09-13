# [H] CVE-2016-10129

## Summary
Severity: High
Advisory: CVE-2016-10129
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-03-24
Source: https://osv.dev/vulnerability/CVE-2016-10129
Type: osv

## Details
The Git Smart Protocol support in libgit2 before 0.24.6 and 0.25.x before 0.25.1 allows remote attackers to cause a denial of service (NULL pointer dereference) via an empty packet line.

## References
- http://www.securityfocus.com/bid/95339
- http://lists.opensuse.org/opensuse-updates/2017-02/msg00030.html
- http://lists.opensuse.org/opensuse-updates/2017-02/msg00036.html
- http://lists.opensuse.org/opensuse-updates/2017-02/msg00072.html
- http://www.openwall.com/lists/oss-security/2017/01/10/5
- http://www.openwall.com/lists/oss-security/2017/01/11/6
- https://github.com/libgit2/libgit2/commit/2fdef641fd0dd2828bd948234ae86de75221a11a
- https://github.com/libgit2/libgit2/commit/84d30d569ada986f3eef527cbdb932643c2dd037
- https://libgit2.github.com/security/
