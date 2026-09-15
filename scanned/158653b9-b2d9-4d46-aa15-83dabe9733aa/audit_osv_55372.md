# [H] CVE-2025-4093

## Summary
Severity: High
Advisory: CVE-2025-4093
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-04-29
Source: https://osv.dev/vulnerability/CVE-2025-4093
Type: osv

## Details
Memory safety bug present in Firefox ESR 128.9, and Thunderbird 128.9. This bug showed evidence of memory corruption and we presume that with enough effort this could have been exploited to run arbitrary code. This vulnerability affects Firefox ESR < 128.10 and Thunderbird < 128.10.

## References
- https://lists.debian.org/debian-lts-announce/2025/05/msg00024.html
- https://www.mozilla.org/security/advisories/mfsa2025-29/
- https://www.mozilla.org/security/advisories/mfsa2025-32/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1894100
