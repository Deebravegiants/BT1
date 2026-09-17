# [C] CVE-2017-5402

## Summary
Severity: Critical
Advisory: CVE-2017-5402
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2017-5402
Type: osv

## Details
A use-after-free can occur when events are fired for a "FontFace" object after the object has been already been destroyed while working with fonts. This results in a potentially exploitable crash. This vulnerability affects Firefox < 52, Firefox ESR < 45.8, Thunderbird < 52, and Thunderbird < 45.8.

## References
- https://www.debian.org/security/2017/dsa-3832
- https://www.mozilla.org/security/advisories/mfsa2017-05/
- https://www.mozilla.org/security/advisories/mfsa2017-06/
- https://www.mozilla.org/security/advisories/mfsa2017-07/
- http://rhn.redhat.com/errata/RHSA-2017-0459.html
- http://rhn.redhat.com/errata/RHSA-2017-0461.html
- http://www.securitytracker.com/id/1037966
- https://security.gentoo.org/glsa/201705-07
- https://www.mozilla.org/security/advisories/mfsa2017-09/
- http://rhn.redhat.com/errata/RHSA-2017-0498.html
- http://www.securityfocus.com/bid/96664
- https://security.gentoo.org/glsa/201705-06
- https://www.debian.org/security/2017/dsa-3805
- https://bugzilla.mozilla.org/show_bug.cgi?id=1334876
