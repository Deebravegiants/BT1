# [M] CVE-2018-5131

## Summary
Severity: Medium
Advisory: CVE-2018-5131
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2018-5131
Type: osv

## Details
Under certain circumstances the "fetch()" API can return transient local copies of resources that were sent with a "no-store" or "no-cache" cache header instead of downloading a copy from the network as it should. This can result in previously stored, locally cached data of a website being accessible to users if they share a common profile while browsing. This vulnerability affects Firefox ESR < 52.7 and Firefox < 59.

## References
- https://lists.debian.org/debian-lts-announce/2018/03/msg00010.html
- https://www.mozilla.org/security/advisories/mfsa2018-06/
- https://security.gentoo.org/glsa/201810-01
- https://usn.ubuntu.com/3596-1/
- https://www.debian.org/security/2018/dsa-4139
- https://www.mozilla.org/security/advisories/mfsa2018-07/
- http://www.securityfocus.com/bid/103388
- http://www.securitytracker.com/id/1040514
- https://access.redhat.com/errata/RHSA-2018:0526
- https://access.redhat.com/errata/RHSA-2018:0527
- https://bugzilla.mozilla.org/show_bug.cgi?id=1440775
