# [H] CVE-2022-22761

## Summary
Severity: High
Advisory: CVE-2022-22761
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-22761
Type: osv

## Details
Web-accessible extension pages (pages with a moz-extension:// scheme) were not correctly enforcing the frame-ancestors directive when it was used in the Web Extension's Content Security Policy. This vulnerability affects Firefox < 97, Thunderbird < 91.6, and Firefox ESR < 91.6.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-04/
- https://www.mozilla.org/security/advisories/mfsa2022-05/
- https://www.mozilla.org/security/advisories/mfsa2022-06/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1745566
