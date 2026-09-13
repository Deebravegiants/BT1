# [M] CVE-2022-38472

## Summary
Severity: Medium
Advisory: CVE-2022-38472
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-38472
Type: osv

## Details
An attacker could have abused XSLT error handling to associate attacker-controlled content with another origin which was displayed in the address bar. This could have been used to fool the user into submitting data intended for the spoofed origin. This vulnerability affects Thunderbird < 102.2, Thunderbird < 91.13, Firefox ESR < 91.13, Firefox ESR < 102.2, and Firefox < 104.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-33/
- https://www.mozilla.org/security/advisories/mfsa2022-34/
- https://www.mozilla.org/security/advisories/mfsa2022-35/
- https://www.mozilla.org/security/advisories/mfsa2022-36/
- https://www.mozilla.org/security/advisories/mfsa2022-37/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1769155
