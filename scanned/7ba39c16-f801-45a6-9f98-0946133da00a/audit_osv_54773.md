# [H] CVE-2024-3864

## Summary
Severity: High
Advisory: CVE-2024-3864
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-16
Source: https://osv.dev/vulnerability/CVE-2024-3864
Type: osv

## Details
Memory safety bug present in Firefox 124, Firefox ESR 115.9, and Thunderbird 115.9. This bug showed evidence of memory corruption and we presume that with enough effort this could have been exploited to run arbitrary code. This vulnerability affects Firefox < 125, Firefox ESR < 115.10, and Thunderbird < 115.10.

## References
- https://www.mozilla.org/security/advisories/mfsa2024-18/
- https://www.mozilla.org/security/advisories/mfsa2024-19/
- https://www.mozilla.org/security/advisories/mfsa2024-20/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1888333
- https://lists.debian.org/debian-lts-announce/2024/04/msg00013.html
- https://lists.debian.org/debian-lts-announce/2024/04/msg00012.html
