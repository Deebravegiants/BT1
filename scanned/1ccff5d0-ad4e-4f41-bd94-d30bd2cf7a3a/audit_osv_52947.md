# [H] CVE-2022-22756

## Summary
Severity: High
Advisory: CVE-2022-22756
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-22756
Type: osv

## Details
If a user was convinced to drag and drop an image to their desktop or other folder, the resulting object could have been changed into an executable script which would have run arbitrary code after the user clicked on it. This vulnerability affects Firefox < 97, Thunderbird < 91.6, and Firefox ESR < 91.6.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-04/
- https://www.mozilla.org/security/advisories/mfsa2022-05/
- https://www.mozilla.org/security/advisories/mfsa2022-06/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1317873
