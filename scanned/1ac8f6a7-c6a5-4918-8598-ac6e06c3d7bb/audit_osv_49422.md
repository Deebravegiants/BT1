# [H] CVE-2019-11757

## Summary
Severity: High
Advisory: CVE-2019-11757
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-01-08
Source: https://osv.dev/vulnerability/CVE-2019-11757
Type: osv

## Details
When following the value's prototype chain, it was possible to retain a reference to a locale, delete it, and subsequently reference it. This resulted in a use-after-free and a potentially exploitable crash. This vulnerability affects Firefox < 70, Thunderbird < 68.2, and Firefox ESR < 68.2.

## References
- https://www.mozilla.org/security/advisories/mfsa2019-33/
- https://www.mozilla.org/security/advisories/mfsa2019-34/
- https://www.mozilla.org/security/advisories/mfsa2019-35/
- https://security.gentoo.org/glsa/202003-10
- https://usn.ubuntu.com/4335-1/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1577107
