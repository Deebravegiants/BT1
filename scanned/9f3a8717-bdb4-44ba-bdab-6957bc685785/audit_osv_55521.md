# [M] CVE-2025-6429

## Summary
Severity: Medium
Advisory: CVE-2025-6429
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:H/A:N)
Published: 2025-06-24
Source: https://osv.dev/vulnerability/CVE-2025-6429
Type: osv

## Details
Firefox could have incorrectly parsed a URL and rewritten it to the youtube.com domain when parsing the URL specified in an `embed` tag.  This could have bypassed website security checks that restricted which domains users were allowed to embed. This vulnerability affects Firefox < 140, Firefox ESR < 128.12, Thunderbird < 140, and Thunderbird < 128.12.

## References
- https://lists.debian.org/debian-lts-announce/2025/06/msg00029.html
- https://lists.debian.org/debian-lts-announce/2025/07/msg00002.html
- https://www.mozilla.org/security/advisories/mfsa2025-51/
- https://www.mozilla.org/security/advisories/mfsa2025-53/
- https://www.mozilla.org/security/advisories/mfsa2025-54/
- https://www.mozilla.org/security/advisories/mfsa2025-55/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1970658
