# [H] CVE-2016-7445

## Summary
Severity: High
Advisory: CVE-2016-7445
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2016-10-03
Source: https://osv.dev/vulnerability/CVE-2016-7445
Type: osv

## Details
convert.c in OpenJPEG before 2.1.2 allows remote attackers to cause a denial of service (NULL pointer dereference and application crash) via vectors involving the variable s.

## References
- http://lists.opensuse.org/opensuse-updates/2016-09/msg00109.html
- http://www.openwall.com/lists/oss-security/2016/09/18/6
- http://www.securityfocus.com/bid/93040
- https://github.com/uclouvain/openjpeg/blob/openjpeg-2.1/CHANGELOG.md
- https://security.gentoo.org/glsa/201612-26
- https://github.com/uclouvain/openjpeg/issues/843
- http://www.openwall.com/lists/oss-security/2016/09/18/4
