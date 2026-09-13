# [H] CVE-2016-3075

## Summary
Severity: High
Advisory: CVE-2016-3075
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-06-01
Source: https://osv.dev/vulnerability/CVE-2016-3075
Type: osv

## Details
Stack-based buffer overflow in the nss_dns implementation of the getnetbyname function in GNU C Library (aka glibc) before 2.24 allows context-dependent attackers to cause a denial of service (stack consumption and application crash) via a long name.

## References
- http://lists.fedoraproject.org/pipermail/package-announce/2016-May/184626.html
- http://lists.opensuse.org/opensuse-updates/2016-06/msg00030.html
- http://lists.opensuse.org/opensuse-updates/2016-07/msg00039.html
- http://www.securityfocus.com/bid/85732
- https://sourceware.org/git/gitweb.cgi?p=glibc.git%3Bh=317b199b4aff8cfa27f2302ab404d2bb5032b9a4
- http://rhn.redhat.com/errata/RHSA-2016-2573.html
- http://www.ubuntu.com/usn/USN-2985-1
- https://security.gentoo.org/glsa/201702-11
- https://sourceware.org/bugzilla/show_bug.cgi?id=19879
