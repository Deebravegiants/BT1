# [M] CVE-2025-0240

## Summary
Severity: Medium
Advisory: CVE-2025-0240
CVSS: 4.0 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2025-01-07
Source: https://osv.dev/vulnerability/CVE-2025-0240
Type: osv

## Details
Parsing a JavaScript module as JSON could, under some circumstances, cause cross-compartment access, which may result in a use-after-free. This vulnerability affects Firefox < 134, Firefox ESR < 128.6, Thunderbird < 134, and Thunderbird < 128.6.

## References
- https://lists.debian.org/debian-lts-announce/2025/01/msg00004.html
- https://www.mozilla.org/security/advisories/mfsa2025-04/
- https://www.mozilla.org/security/advisories/mfsa2025-05/
- https://www.mozilla.org/security/advisories/mfsa2025-01/
- https://www.mozilla.org/security/advisories/mfsa2025-02/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1929623
