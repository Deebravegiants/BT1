# [H] CVE-2018-16875

## Summary
Severity: High
Advisory: CVE-2018-16875
Aliases: GO-2022-0191
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-12-14
Source: https://osv.dev/vulnerability/CVE-2018-16875
Type: osv

## Details
The crypto/x509 package of Go before 1.10.6 and 1.11.x before 1.11.3 does not limit the amount of work performed for each chain verification, which might allow attackers to craft pathological inputs leading to a CPU denial of service. Go TLS servers accepting client certificates and TLS clients are affected.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00060.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00011.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00010.html
- https://groups.google.com/forum/?pli=1#%21topic/golang-announce/Kw31K8G7Fi0
- http://lists.opensuse.org/opensuse-security-announce/2019-03/msg00044.html
- http://www.securityfocus.com/bid/106230
- https://security.gentoo.org/glsa/201812-09
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2018-16875
