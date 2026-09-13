# [M] CVE-2022-45416

## Summary
Severity: Medium
Advisory: CVE-2022-45416
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-45416
Type: osv

## Details
Keyboard events reference strings like "KeyA" that were at fixed, known, and widely-spread addresses. Cache-based timing attacks such as Prime+Probe could have possibly figured out which keys were being pressed. This vulnerability affects Firefox ESR < 102.5, Thunderbird < 102.5, and Firefox < 107.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-48/
- https://www.mozilla.org/security/advisories/mfsa2022-49/
- https://www.mozilla.org/security/advisories/mfsa2022-47/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1793676
