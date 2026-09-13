# [C] CVE-2017-7792

## Summary
Severity: Critical
Advisory: CVE-2017-7792
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2017-7792
Type: osv

## Details
A buffer overflow will occur when viewing a certificate in the certificate manager if the certificate has an extremely long object identifier (OID). This results in a potentially exploitable crash. This vulnerability affects Thunderbird < 52.3, Firefox ESR < 52.3, and Firefox < 55.

## References
- http://www.securityfocus.com/bid/100206
- http://www.securitytracker.com/id/1039124
- https://www.debian.org/security/2017/dsa-3928
- https://www.debian.org/security/2017/dsa-3968
- https://www.mozilla.org/security/advisories/mfsa2017-20/
- https://access.redhat.com/errata/RHSA-2017:2456
- https://access.redhat.com/errata/RHSA-2017:2534
- https://security.gentoo.org/glsa/201803-14
- https://www.mozilla.org/security/advisories/mfsa2017-18/
- https://www.mozilla.org/security/advisories/mfsa2017-19/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1368652
