# [H] CVE-2022-22763

## Summary
Severity: High
Advisory: CVE-2022-22763
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-22763
Type: osv

## Details
When a worker is shutdown, it was possible to cause script to run late in the lifecycle, at a point after where it should not be possible. This vulnerability affects Firefox < 96, Thunderbird < 91.6, and Firefox ESR < 91.6.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-01/
- https://www.mozilla.org/security/advisories/mfsa2022-05/
- https://www.mozilla.org/security/advisories/mfsa2022-06/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1740534
