# [C] CVE-2022-45406

## Summary
Severity: Critical
Advisory: CVE-2022-45406
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-45406
Type: osv

## Details
If an out-of-memory condition occurred when creating a JavaScript global, a JavaScript realm may be deleted while references to it lived on in a BaseShape. This could lead to a use-after-free causing a potentially exploitable crash. This vulnerability affects Firefox ESR < 102.5, Thunderbird < 102.5, and Firefox < 107.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-47/
- https://www.mozilla.org/security/advisories/mfsa2022-48/
- https://www.mozilla.org/security/advisories/mfsa2022-49/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1791975
