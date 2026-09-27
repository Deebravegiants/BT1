# [H] CVE-2019-10164

## Summary
Severity: High
Advisory: CVE-2019-10164
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-26
Source: https://osv.dev/vulnerability/CVE-2019-10164
Type: osv

## Details
PostgreSQL versions 10.x before 10.9 and versions 11.x before 11.4 are vulnerable to a stack-based buffer overflow. Any authenticated user can overflow a stack-based buffer by changing the user's own password to a purpose-crafted value. This often suffices to execute arbitrary code as the PostgreSQL operating system account.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MAGE6H4FWLKFLHLWVYNPYGQRPIXTUWGB/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TTKEHXGDXYYD6WYDIIQJP4GDQJSENDJK/
- https://security.gentoo.org/glsa/202003-03
- https://www.postgresql.org/about/news/1949/
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00035.html
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10164
