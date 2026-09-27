# [H] CVE-2017-5444

## Summary
Severity: High
Advisory: CVE-2017-5444
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-06-11
Source: https://osv.dev/vulnerability/CVE-2017-5444
Type: osv

## Details
A buffer overflow vulnerability while parsing "application/http-index-format" format content when the header contains improperly formatted data. This allows for an out-of-bounds read of data from memory. This vulnerability affects Thunderbird < 52.1, Firefox ESR < 45.9, Firefox ESR < 52.1, and Firefox < 53.

## References
- https://www.mozilla.org/security/advisories/mfsa2017-11/
- http://www.securitytracker.com/id/1038320
- https://access.redhat.com/errata/RHSA-2017:1104
- https://access.redhat.com/errata/RHSA-2017:1106
- https://www.debian.org/security/2017/dsa-3831
- https://www.mozilla.org/security/advisories/mfsa2017-10/
- https://www.mozilla.org/security/advisories/mfsa2017-12/
- https://www.mozilla.org/security/advisories/mfsa2017-13/
- http://www.securityfocus.com/bid/97940
- https://access.redhat.com/errata/RHSA-2017:1201
- https://bugzilla.mozilla.org/show_bug.cgi?id=1344461
