# [C] CVE-2017-5465

## Summary
Severity: Critical
Advisory: CVE-2017-5465
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2017-5465
Type: osv

## Details
An out-of-bounds read while processing SVG content in "ConvolvePixel". This results in a crash and also allows for otherwise inaccessible memory being copied into SVG graphic content, which could then displayed. This vulnerability affects Thunderbird < 52.1, Firefox ESR < 45.9, Firefox ESR < 52.1, and Firefox < 53.

## References
- https://access.redhat.com/errata/RHSA-2017:1104
- https://access.redhat.com/errata/RHSA-2017:1106
- https://www.mozilla.org/security/advisories/mfsa2017-10/
- https://www.mozilla.org/security/advisories/mfsa2017-11/
- https://www.mozilla.org/security/advisories/mfsa2017-12/
- http://www.securityfocus.com/bid/97940
- http://www.securitytracker.com/id/1038320
- https://access.redhat.com/errata/RHSA-2017:1201
- https://www.debian.org/security/2017/dsa-3831
- https://www.mozilla.org/security/advisories/mfsa2017-13/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1347617
- https://www.exploit-db.com/exploits/42072/
