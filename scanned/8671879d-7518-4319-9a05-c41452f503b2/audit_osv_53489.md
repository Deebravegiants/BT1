# [M] CVE-2022-45418

## Summary
Severity: Medium
Advisory: CVE-2022-45418
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-45418
Type: osv

## Details
If a custom mouse cursor is specified in CSS, under certain circumstances the cursor could have been drawn over the browser UI, resulting in potential user confusion or spoofing attacks. This vulnerability affects Firefox ESR < 102.5, Thunderbird < 102.5, and Firefox < 107.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-47/
- https://www.mozilla.org/security/advisories/mfsa2022-48/
- https://www.mozilla.org/security/advisories/mfsa2022-49/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1795815
