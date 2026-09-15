# [M] CVE-2017-5407

## Summary
Severity: Medium
Advisory: CVE-2017-5407
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2017-5407
Type: osv

## Details
Using SVG filters that don't use the fixed point math implementation on a target iframe, a malicious page can extract pixel values from a targeted user. This can be used to extract history information and read text values across domains. This violates same-origin policy and leads to information disclosure. This vulnerability affects Firefox < 52, Firefox ESR < 45.8, Thunderbird < 52, and Thunderbird < 45.8.

## References
- https://www.debian.org/security/2017/dsa-3805
- https://www.debian.org/security/2017/dsa-3832
- https://www.mozilla.org/security/advisories/mfsa2017-09/
- http://rhn.redhat.com/errata/RHSA-2017-0459.html
- http://rhn.redhat.com/errata/RHSA-2017-0461.html
- http://rhn.redhat.com/errata/RHSA-2017-0498.html
- http://www.securitytracker.com/id/1037966
- https://www.mozilla.org/security/advisories/mfsa2017-05/
- https://www.mozilla.org/security/advisories/mfsa2017-06/
- https://www.mozilla.org/security/advisories/mfsa2017-07/
- http://www.securityfocus.com/bid/96693
- https://security.gentoo.org/glsa/201705-06
- https://security.gentoo.org/glsa/201705-07
- https://bugzilla.mozilla.org/show_bug.cgi?id=1336622
