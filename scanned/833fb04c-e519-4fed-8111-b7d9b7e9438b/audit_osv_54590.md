# [H] CVE-2024-1546

## Summary
Severity: High
Advisory: CVE-2024-1546
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-02-20
Source: https://osv.dev/vulnerability/CVE-2024-1546
Type: osv

## Details
When storing and re-accessing data on a networking channel, the length of buffers may have been confused, resulting in an out-of-bounds memory read. This vulnerability affects Firefox < 123, Firefox ESR < 115.8, and Thunderbird < 115.8.

## References
- https://www.mozilla.org/security/advisories/mfsa2024-05/
- https://www.mozilla.org/security/advisories/mfsa2024-06/
- https://www.mozilla.org/security/advisories/mfsa2024-07/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1843752
- https://lists.debian.org/debian-lts-announce/2024/03/msg00000.html
- https://lists.debian.org/debian-lts-announce/2024/03/msg00001.html
