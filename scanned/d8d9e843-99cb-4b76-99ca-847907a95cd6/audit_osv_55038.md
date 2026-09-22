# [M] CVE-2024-9398

## Summary
Severity: Medium
Advisory: CVE-2024-9398
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-10-01
Source: https://osv.dev/vulnerability/CVE-2024-9398
Type: osv

## Details
By checking the result of calls to `window.open` with specifically set protocol handlers, an attacker could determine if the application which implements that protocol handler is installed. This vulnerability affects Firefox < 131, Firefox ESR < 128.3, Thunderbird < 128.3, and Thunderbird < 131.

## References
- https://www.mozilla.org/security/advisories/mfsa2024-46/
- https://www.mozilla.org/security/advisories/mfsa2024-47/
- https://www.mozilla.org/security/advisories/mfsa2024-49/
- https://www.mozilla.org/security/advisories/mfsa2024-50/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1881037
