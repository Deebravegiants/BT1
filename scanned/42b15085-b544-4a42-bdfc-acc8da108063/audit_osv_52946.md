# [M] CVE-2022-22754

## Summary
Severity: Medium
Advisory: CVE-2022-22754
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-22754
Type: osv

## Details
If a user installed an extension of a particular type, the extension could have auto-updated itself and while doing so, bypass the prompt which grants the new version the new requested permissions. This vulnerability affects Firefox < 97, Thunderbird < 91.6, and Firefox ESR < 91.6.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-04/
- https://www.mozilla.org/security/advisories/mfsa2022-05/
- https://www.mozilla.org/security/advisories/mfsa2022-06/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1750565
