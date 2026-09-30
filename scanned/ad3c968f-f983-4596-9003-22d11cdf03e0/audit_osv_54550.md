# [H] CVE-2024-10466

## Summary
Severity: High
Advisory: CVE-2024-10466
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-10-29
Source: https://osv.dev/vulnerability/CVE-2024-10466
Type: osv

## Details
By sending a specially crafted push message, a remote server could have hung the parent process, causing the browser to become unresponsive. This vulnerability affects Firefox < 132, Firefox ESR < 128.4, Thunderbird < 128.4, and Thunderbird < 132.

## References
- https://lists.debian.org/debian-lts-announce/2024/10/msg00034.html
- https://lists.debian.org/debian-lts-announce/2024/11/msg00001.html
- https://www.mozilla.org/security/advisories/mfsa2024-55/
- https://www.mozilla.org/security/advisories/mfsa2024-56/
- https://www.mozilla.org/security/advisories/mfsa2024-58/
- https://www.mozilla.org/security/advisories/mfsa2024-59/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1924154
