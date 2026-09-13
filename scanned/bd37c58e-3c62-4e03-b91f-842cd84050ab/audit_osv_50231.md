# [M] CVE-2019-9817

## Summary
Severity: Medium
Advisory: CVE-2019-9817
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2019-07-23
Source: https://osv.dev/vulnerability/CVE-2019-9817
Type: osv

## Details
Images from a different domain can be read using a canvas object in some circumstances. This could be used to steal image data from a different site in violation of same-origin policy. This vulnerability affects Thunderbird < 60.7, Firefox < 67, and Firefox ESR < 60.7.

## References
- https://www.mozilla.org/security/advisories/mfsa2019-13/
- https://www.mozilla.org/security/advisories/mfsa2019-14/
- https://www.mozilla.org/security/advisories/mfsa2019-15/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1540221
