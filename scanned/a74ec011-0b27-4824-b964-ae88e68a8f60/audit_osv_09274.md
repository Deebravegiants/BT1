# [M] CVE-2016-9318

## Summary
Severity: Medium
Advisory: CVE-2016-9318
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2016-11-16
Source: https://osv.dev/vulnerability/CVE-2016-9318
Type: osv

## Details
libxml2 2.9.4 and earlier, as used in XMLSec 1.2.23 and earlier and other products, does not offer a flag directly indicating that the current document may be read but other files may not be opened, which makes it easier for remote attackers to conduct XML External Entity (XXE) attacks via a crafted document.

## References
- https://lists.debian.org/debian-lts-announce/2022/04/msg00004.html
- http://www.securityfocus.com/bid/94347
- https://security.gentoo.org/glsa/201711-01
- https://usn.ubuntu.com/3739-1/
- https://usn.ubuntu.com/3739-2/
- https://bugzilla.gnome.org/show_bug.cgi?id=772726
- https://github.com/lsh123/xmlsec/issues/43
