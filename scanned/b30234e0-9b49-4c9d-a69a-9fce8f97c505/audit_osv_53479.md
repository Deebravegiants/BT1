# [M] CVE-2022-45404

## Summary
Severity: Medium
Advisory: CVE-2022-45404
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-45404
Type: osv

## Details
Through a series of popup and <code>window.print()</code> calls, an attacker can cause a window to go fullscreen without the user seeing the notification prompt, resulting in potential user confusion or spoofing attacks. This vulnerability affects Firefox ESR < 102.5, Thunderbird < 102.5, and Firefox < 107.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-47/
- https://www.mozilla.org/security/advisories/mfsa2022-48/
- https://www.mozilla.org/security/advisories/mfsa2022-49/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1790815
