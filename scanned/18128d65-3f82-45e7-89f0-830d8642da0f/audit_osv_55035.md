# [H] CVE-2024-9394

## Summary
Severity: High
Advisory: CVE-2024-9394
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-10-01
Source: https://osv.dev/vulnerability/CVE-2024-9394
Type: osv

## Details
An attacker could, via a specially crafted multipart response, execute arbitrary JavaScript under the `resource://devtools` origin.  This could allow them to access cross-origin JSON content. This access is limited to "same site" documents by the Site Isolation feature on desktop clients, but full cross-origin access is possible on Android versions. This vulnerability affects Firefox < 131, Firefox ESR < 128.3, Firefox ESR < 115.16, Thunderbird < 128.3, and Thunderbird < 131.

## References
- https://lists.debian.org/debian-lts-announce/2024/10/msg00006.html
- https://lists.debian.org/debian-lts-announce/2024/10/msg00004.html
- https://www.mozilla.org/security/advisories/mfsa2024-46/
- https://www.mozilla.org/security/advisories/mfsa2024-47/
- https://www.mozilla.org/security/advisories/mfsa2024-48/
- https://www.mozilla.org/security/advisories/mfsa2024-49/
- https://www.mozilla.org/security/advisories/mfsa2024-50/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1918874
