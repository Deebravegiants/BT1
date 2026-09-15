# [M] CVE-2022-29911

## Summary
Severity: Medium
Advisory: CVE-2022-29911
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-29911
Type: osv

## Details
An improper implementation of the new iframe sandbox keyword <code>allow-top-navigation-by-user-activation</code> could lead to script execution without <code>allow-scripts</code> being present. This vulnerability affects Thunderbird < 91.9, Firefox ESR < 91.9, and Firefox < 100.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-16/
- https://www.mozilla.org/security/advisories/mfsa2022-17/
- https://www.mozilla.org/security/advisories/mfsa2022-18/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1761981
