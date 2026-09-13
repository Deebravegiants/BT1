# [C] CVE-2017-7786

## Summary
Severity: Critical
Advisory: CVE-2017-7786
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2017-7786
Type: osv

## Details
A buffer overflow can occur when the image renderer attempts to paint non-displayable SVG elements. This results in a potentially exploitable crash. This vulnerability affects Thunderbird < 52.3, Firefox ESR < 52.3, and Firefox < 55.

## References
- https://www.mozilla.org/security/advisories/mfsa2017-18/
- https://www.mozilla.org/security/advisories/mfsa2017-19/
- https://www.mozilla.org/security/advisories/mfsa2017-20/
- http://www.securityfocus.com/bid/100206
- http://www.securitytracker.com/id/1039124
- https://access.redhat.com/errata/RHSA-2017:2456
- https://access.redhat.com/errata/RHSA-2017:2534
- https://www.debian.org/security/2017/dsa-3928
- https://security.gentoo.org/glsa/201803-14
- https://www.debian.org/security/2017/dsa-3968
- https://bugzilla.mozilla.org/show_bug.cgi?id=1365189
