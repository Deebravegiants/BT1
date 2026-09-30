# [M] CVE-2023-25730

## Summary
Severity: Medium
Advisory: CVE-2023-25730
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N)
Published: 2023-06-02
Source: https://osv.dev/vulnerability/CVE-2023-25730
Type: osv

## Details
A background script invoking <code>requestFullscreen</code> and then blocking the main thread could force the browser into fullscreen mode indefinitely, resulting in potential user confusion or spoofing attacks. This vulnerability affects Firefox < 110, Thunderbird < 102.8, and Firefox ESR < 102.8.

## References
- https://www.mozilla.org/security/advisories/mfsa2023-05/
- https://www.mozilla.org/security/advisories/mfsa2023-06/
- https://www.mozilla.org/security/advisories/mfsa2023-07/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1794622
