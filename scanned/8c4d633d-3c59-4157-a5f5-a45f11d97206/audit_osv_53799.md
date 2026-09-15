# [H] CVE-2023-25737

## Summary
Severity: High
Advisory: CVE-2023-25737
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-06-02
Source: https://osv.dev/vulnerability/CVE-2023-25737
Type: osv

## Details
An invalid downcast from <code>nsTextNode</code> to <code>SVGElement</code> could have lead to undefined behavior. This vulnerability affects Firefox < 110, Thunderbird < 102.8, and Firefox ESR < 102.8.

## References
- https://www.mozilla.org/security/advisories/mfsa2023-05/
- https://www.mozilla.org/security/advisories/mfsa2023-06/
- https://www.mozilla.org/security/advisories/mfsa2023-07/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1811464
