# [H] CVE-2021-3516

## Summary
Severity: High
Advisory: CVE-2021-3516
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-06-01
Source: https://osv.dev/vulnerability/CVE-2021-3516
Type: osv

## Details
There's a flaw in libxml2's xmllint in versions before 2.9.11. An attacker who is able to submit a crafted file to be processed by xmllint could trigger a use-after-free. The greatest impact of this flaw is to confidentiality, integrity, and availability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BZOMV5J4PMZAORVT64BKLV6YIZAFDGX6/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/QVM4UJ3376I6ZVOYMHBNX4GY3NIV52WV/
- https://lists.debian.org/debian-lts-announce/2021/05/msg00008.html
- https://security.gentoo.org/glsa/202107-05
- https://security.netapp.com/advisory/ntap-20210716-0005/
- https://bugzilla.redhat.com/show_bug.cgi?id=1954225
- https://gitlab.gnome.org/GNOME/libxml2/-/issues/230
- https://gitlab.gnome.org/GNOME/libxml2/-/commit/1358d157d0bd83be1dfe356a69213df9fac0b539
- https://www.oracle.com/security-alerts/cpujan2022.html
