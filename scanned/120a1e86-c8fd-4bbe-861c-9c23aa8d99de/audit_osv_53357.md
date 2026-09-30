# [M] CVE-2022-40956

## Summary
Severity: Medium
Advisory: CVE-2022-40956
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-40956
Type: osv

## Details
When injecting an HTML base element, some requests would ignore the CSP's base-uri settings and accept the injected element's base instead. This vulnerability affects Firefox ESR < 102.3, Thunderbird < 102.3, and Firefox < 105.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-40/
- https://www.mozilla.org/security/advisories/mfsa2022-41/
- https://www.mozilla.org/security/advisories/mfsa2022-42/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1770094
