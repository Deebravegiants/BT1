# [M] CVE-2020-26965

## Summary
Severity: Medium
Advisory: CVE-2020-26965
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2020-12-09
Source: https://osv.dev/vulnerability/CVE-2020-26965
Type: osv

## Details
Some websites have a feature "Show Password" where clicking a button will change a password field into a textbook field, revealing the typed password. If, when using a software keyboard that remembers user input, a user typed their password and used that feature, the type of the password field was changed, resulting in a keyboard layout change and the possibility for the software keyboard to remember the typed password. This vulnerability affects Firefox < 83, Firefox ESR < 78.5, and Thunderbird < 78.5.

## References
- https://www.mozilla.org/security/advisories/mfsa2020-50/
- https://www.mozilla.org/security/advisories/mfsa2020-51/
- https://www.mozilla.org/security/advisories/mfsa2020-52/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1661617
