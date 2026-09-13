# [H] CVE-2020-26959

## Summary
Severity: High
Advisory: CVE-2020-26959
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-12-09
Source: https://osv.dev/vulnerability/CVE-2020-26959
Type: osv

## Details
During browser shutdown, reference decrementing could have occured on a previously freed object, resulting in a use-after-free, memory corruption, and a potentially exploitable crash. This vulnerability affects Firefox < 83, Firefox ESR < 78.5, and Thunderbird < 78.5.

## References
- https://www.mozilla.org/security/advisories/mfsa2020-51/
- https://www.mozilla.org/security/advisories/mfsa2020-52/
- https://www.mozilla.org/security/advisories/mfsa2020-50/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1669466
