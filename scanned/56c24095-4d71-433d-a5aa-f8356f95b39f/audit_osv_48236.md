# [M] CVE-2017-5383

## Summary
Severity: Medium
Advisory: CVE-2017-5383
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2017-5383
Type: osv

## Details
URLs containing certain unicode glyphs for alternative hyphens and quotes do not properly trigger punycode display, allowing for domain name spoofing attacks in the location bar. This vulnerability affects Thunderbird < 45.7, Firefox ESR < 45.7, and Firefox < 51.

## References
- http://www.securityfocus.com/bid/95769
- https://security.gentoo.org/glsa/201702-13
- https://security.gentoo.org/glsa/201702-22
- https://www.debian.org/security/2017/dsa-3771
- https://www.mozilla.org/security/advisories/mfsa2017-03/
- http://rhn.redhat.com/errata/RHSA-2017-0190.html
- http://rhn.redhat.com/errata/RHSA-2017-0238.html
- http://www.securitytracker.com/id/1037693
- https://www.debian.org/security/2017/dsa-3832
- https://www.mozilla.org/security/advisories/mfsa2017-01/
- https://www.mozilla.org/security/advisories/mfsa2017-02/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1323338
- https://bugzilla.mozilla.org/show_bug.cgi?id=1324716
