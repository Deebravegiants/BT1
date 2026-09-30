# [M] CVE-2025-4087

## Summary
Severity: Medium
Advisory: CVE-2025-4087
CVSS: 4.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2025-04-29
Source: https://osv.dev/vulnerability/CVE-2025-4087
Type: osv

## Details
A vulnerability was identified in Thunderbird where XPath parsing could trigger undefined behavior due to missing null checks during attribute access. This could lead to out-of-bounds read access and potentially, memory corruption. This vulnerability affects Firefox < 138, Firefox ESR < 128.10, Thunderbird < 138, and Thunderbird < 128.10.

## References
- https://lists.debian.org/debian-lts-announce/2025/05/msg00024.html
- https://www.mozilla.org/security/advisories/mfsa2025-28/
- https://www.mozilla.org/security/advisories/mfsa2025-29/
- https://www.mozilla.org/security/advisories/mfsa2025-31/
- https://www.mozilla.org/security/advisories/mfsa2025-32/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1952465
