# [C] CVE-2025-11710

## Summary
Severity: Critical
Advisory: CVE-2025-11710
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-10-14
Source: https://osv.dev/vulnerability/CVE-2025-11710
Type: osv

## Details
A compromised web process using malicious IPC messages could have caused the privileged browser process to reveal blocks of its memory to the compromised process. This vulnerability affects Firefox < 144, Firefox ESR < 115.29, Firefox ESR < 140.4, Thunderbird < 144, and Thunderbird < 140.4.

## References
- https://lists.debian.org/debian-lts-announce/2025/10/msg00015.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00031.html
- https://www.mozilla.org/security/advisories/mfsa2025-83/
- https://www.mozilla.org/security/advisories/mfsa2025-84/
- https://www.mozilla.org/security/advisories/mfsa2025-85/
- https://www.mozilla.org/security/advisories/mfsa2025-81/
- https://www.mozilla.org/security/advisories/mfsa2025-82/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1989899
