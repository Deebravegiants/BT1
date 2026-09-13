# [M] CVE-2024-10464

## Summary
Severity: Medium
Advisory: CVE-2024-10464
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-10-29
Source: https://osv.dev/vulnerability/CVE-2024-10464
Type: osv

## Details
Repeated writes to history interface attributes could have been used to cause a Denial of Service condition in the browser. This was addressed by introducing rate-limiting to this API. This vulnerability affects Firefox < 132, Firefox ESR < 128.4, Thunderbird < 128.4, and Thunderbird < 132.

## References
- https://lists.debian.org/debian-lts-announce/2024/10/msg00034.html
- https://lists.debian.org/debian-lts-announce/2024/11/msg00001.html
- https://www.mozilla.org/security/advisories/mfsa2024-55/
- https://www.mozilla.org/security/advisories/mfsa2024-56/
- https://www.mozilla.org/security/advisories/mfsa2024-58/
- https://www.mozilla.org/security/advisories/mfsa2024-59/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1913000
