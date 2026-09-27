# [M] CVE-2023-37207

## Summary
Severity: Medium
Advisory: CVE-2023-37207
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2023-07-05
Source: https://osv.dev/vulnerability/CVE-2023-37207
Type: osv

## Details
A website could have obscured the fullscreen notification by using a URL with a scheme handled by an external program, such as a mailto URL. This could have led to user confusion and possible spoofing attacks. This vulnerability affects Firefox < 115, Firefox ESR < 102.13, and Thunderbird < 102.13.

## References
- https://lists.debian.org/debian-lts-announce/2023/07/msg00015.html
- https://www.mozilla.org/security/advisories/mfsa2023-23/
- https://www.mozilla.org/security/advisories/mfsa2023-24/
- https://lists.debian.org/debian-lts-announce/2023/07/msg00006.html
- https://www.debian.org/security/2023/dsa-5450
- https://www.debian.org/security/2023/dsa-5451
- https://www.mozilla.org/security/advisories/mfsa2023-22/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1816287
