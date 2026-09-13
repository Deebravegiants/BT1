# [M] CVE-2024-1551

## Summary
Severity: Medium
Advisory: CVE-2024-1551
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2024-02-20
Source: https://osv.dev/vulnerability/CVE-2024-1551
Type: osv

## Details
Set-Cookie response headers were being incorrectly honored in multipart HTTP responses. If an attacker could control the Content-Type response header, as well as control part of the response body, they could inject Set-Cookie response headers that would have been honored by the browser. This vulnerability affects Firefox < 123, Firefox ESR < 115.8, and Thunderbird < 115.8.

## References
- https://www.mozilla.org/security/advisories/mfsa2024-07/
- https://lists.debian.org/debian-lts-announce/2024/03/msg00000.html
- https://lists.debian.org/debian-lts-announce/2024/03/msg00001.html
- https://www.mozilla.org/security/advisories/mfsa2024-05/
- https://www.mozilla.org/security/advisories/mfsa2024-06/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1864385
