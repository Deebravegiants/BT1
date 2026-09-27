# [H] CVE-2022-22740

## Summary
Severity: High
Advisory: CVE-2022-22740
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-22740
Type: osv

## Details
Certain network request objects were freed too early when releasing a network request handle. This could have lead to a use-after-free causing a potentially exploitable crash. This vulnerability affects Firefox ESR < 91.5, Firefox < 96, and Thunderbird < 91.5.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-01/
- https://www.mozilla.org/security/advisories/mfsa2022-02/
- https://www.mozilla.org/security/advisories/mfsa2022-03/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1742334
