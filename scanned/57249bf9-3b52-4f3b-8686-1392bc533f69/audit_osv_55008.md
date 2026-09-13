# [C] CVE-2024-8381

## Summary
Severity: Critical
Advisory: CVE-2024-8381
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-03
Source: https://osv.dev/vulnerability/CVE-2024-8381
Type: osv

## Details
A potentially exploitable type confusion could be triggered when looking up a property name on an object being used as the `with` environment. This vulnerability affects Firefox < 130, Firefox ESR < 128.2, Firefox ESR < 115.15, Thunderbird < 128.2, and Thunderbird < 115.15.

## References
- https://lists.debian.org/debian-lts-announce/2024/09/msg00012.html
- https://lists.debian.org/debian-lts-announce/2024/09/msg00025.html
- https://www.mozilla.org/security/advisories/mfsa2024-39/
- https://www.mozilla.org/security/advisories/mfsa2024-40/
- https://www.mozilla.org/security/advisories/mfsa2024-41/
- https://www.mozilla.org/security/advisories/mfsa2024-43/
- https://www.mozilla.org/security/advisories/mfsa2024-44/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1912715
