# [M] CVE-2022-42929

## Summary
Severity: Medium
Advisory: CVE-2022-42929
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-42929
Type: osv

## Details
If a website called `window.print()` in a particular way, it could cause a denial of service of the browser, which may persist beyond browser restart depending on the user's session restore settings. This vulnerability affects Firefox < 106, Firefox ESR < 102.4, and Thunderbird < 102.4.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-44/
- https://www.mozilla.org/security/advisories/mfsa2022-45/
- https://www.mozilla.org/security/advisories/mfsa2022-46/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1789439
