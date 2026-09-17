# [M] CVE-2024-3861

## Summary
Severity: Medium
Advisory: CVE-2024-3861
CVSS: 4.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-04-16
Source: https://osv.dev/vulnerability/CVE-2024-3861
Type: osv

## Details
If an AlignedBuffer were assigned to itself, the subsequent self-move could result in an incorrect reference count and later use-after-free. This vulnerability affects Firefox < 125, Firefox ESR < 115.10, and Thunderbird < 115.10.

## References
- https://lists.debian.org/debian-lts-announce/2024/04/msg00012.html
- https://lists.debian.org/debian-lts-announce/2024/04/msg00013.html
- https://www.mozilla.org/security/advisories/mfsa2024-18/
- https://www.mozilla.org/security/advisories/mfsa2024-19/
- https://www.mozilla.org/security/advisories/mfsa2024-20/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1883158
