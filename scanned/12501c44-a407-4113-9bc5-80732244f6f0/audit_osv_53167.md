# [M] CVE-2022-31742

## Summary
Severity: Medium
Advisory: CVE-2022-31742
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-31742
Type: osv

## Details
An attacker could have exploited a timing attack by sending a large number of allowCredential entries and detecting the difference between invalid key handles and cross-origin key handles. This could have led to cross-origin account linking in violation of WebAuthn goals. This vulnerability affects Thunderbird < 91.10, Firefox < 101, and Firefox ESR < 91.10.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-20/
- https://www.mozilla.org/security/advisories/mfsa2022-21/
- https://www.mozilla.org/security/advisories/mfsa2022-22/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1730434
