# [H] CVE-2023-37202

## Summary
Severity: High
Advisory: CVE-2023-37202
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-07-05
Source: https://osv.dev/vulnerability/CVE-2023-37202
Type: osv

## Details
Cross-compartment wrappers wrapping a scripted proxy could have caused objects from other compartments to be stored in the main compartment resulting in a use-after-free. This vulnerability affects Firefox < 115, Firefox ESR < 102.13, and Thunderbird < 102.13.

## References
- https://lists.debian.org/debian-lts-announce/2023/07/msg00015.html
- https://www.mozilla.org/security/advisories/mfsa2023-24/
- https://lists.debian.org/debian-lts-announce/2023/07/msg00006.html
- https://www.debian.org/security/2023/dsa-5450
- https://www.debian.org/security/2023/dsa-5451
- https://www.mozilla.org/security/advisories/mfsa2023-22/
- https://www.mozilla.org/security/advisories/mfsa2023-23/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1834711
