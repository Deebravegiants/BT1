# [M] CVE-2023-6206

## Summary
Severity: Medium
Advisory: CVE-2023-6206
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N)
Published: 2023-11-21
Source: https://osv.dev/vulnerability/CVE-2023-6206
Type: osv

## Details
The black fade animation when exiting fullscreen is roughly the length of the anti-clickjacking delay on permission prompts. It was possible to use this fact to surprise users by luring them to click where the permission grant button would be about to appear. This vulnerability affects Firefox < 120, Firefox ESR < 115.5.0, and Thunderbird < 115.5.

## References
- https://lists.debian.org/debian-lts-announce/2023/11/msg00030.html
- https://www.debian.org/security/2023/dsa-5561
- https://www.mozilla.org/security/advisories/mfsa2023-49/
- https://www.mozilla.org/security/advisories/mfsa2023-50/
- https://www.mozilla.org/security/advisories/mfsa2023-52/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1857430
- https://lists.debian.org/debian-lts-announce/2023/11/msg00017.html
