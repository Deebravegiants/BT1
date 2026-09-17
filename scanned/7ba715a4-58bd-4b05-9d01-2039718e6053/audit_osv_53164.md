# [M] CVE-2022-31738

## Summary
Severity: Medium
Advisory: CVE-2022-31738
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-31738
Type: osv

## Details
When exiting fullscreen mode, an iframe could have confused the browser about the current state of fullscreen, resulting in potential user confusion or spoofing attacks. This vulnerability affects Thunderbird < 91.10, Firefox < 101, and Firefox ESR < 91.10.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-20/
- https://www.mozilla.org/security/advisories/mfsa2022-21/
- https://www.mozilla.org/security/advisories/mfsa2022-22/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1756388
