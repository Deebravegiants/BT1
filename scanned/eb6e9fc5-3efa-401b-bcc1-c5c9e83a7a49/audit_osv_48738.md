# [H] CVE-2018-12371

## Summary
Severity: High
Advisory: CVE-2018-12371
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-07-09
Source: https://osv.dev/vulnerability/CVE-2018-12371
Type: osv

## Details
An integer overflow vulnerability in the Skia library when allocating memory for edge builders on some systems with at least 16 GB of RAM. This results in the use of uninitialized memory, resulting in a potentially exploitable crash. This vulnerability affects Firefox ESR < 60.1, Thunderbird < 60, and Firefox < 61.

## References
- https://www.mozilla.org/security/advisories/mfsa2018-15/
- https://www.mozilla.org/security/advisories/mfsa2018-16/
- https://www.mozilla.org/security/advisories/mfsa2018-19/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1465686
