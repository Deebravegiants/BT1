# [C] CVE-2017-5447

## Summary
Severity: Critical
Advisory: CVE-2017-5447
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2017-5447
Type: osv

## Details
An out-of-bounds read during the processing of glyph widths during text layout. This results in a potentially exploitable crash and could allow an attacker to read otherwise inaccessible memory. This vulnerability affects Thunderbird < 52.1, Firefox ESR < 45.9, Firefox ESR < 52.1, and Firefox < 53.

## References
- http://www.securitytracker.com/id/1038320
- https://access.redhat.com/errata/RHSA-2017:1106
- https://www.debian.org/security/2017/dsa-3831
- https://www.mozilla.org/security/advisories/mfsa2017-10/
- https://www.mozilla.org/security/advisories/mfsa2017-12/
- https://www.mozilla.org/security/advisories/mfsa2017-13/
- http://www.securityfocus.com/bid/97940
- https://access.redhat.com/errata/RHSA-2017:1104
- https://access.redhat.com/errata/RHSA-2017:1201
- https://www.mozilla.org/security/advisories/mfsa2017-11/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1343552
- https://www.exploit-db.com/exploits/42071/
