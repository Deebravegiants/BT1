# [H] CVE-2023-29541

## Summary
Severity: High
Advisory: CVE-2023-29541
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2023-06-02
Source: https://osv.dev/vulnerability/CVE-2023-29541
Type: osv

## Details
Firefox did not properly handle downloads of files ending in <code>.desktop</code>, which can be interpreted to run attacker-controlled commands. <br>*This bug only affects Firefox for Linux on certain Distributions. Other operating systems are unaffected, and Mozilla is unable to enumerate all affected Linux Distributions.*. This vulnerability affects Firefox < 112, Focus for Android < 112, Firefox ESR < 102.10, Firefox for Android < 112, and Thunderbird < 102.10.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/29xxx/CVE-2023-29541.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-29541
- https://www.mozilla.org/security/advisories/mfsa2023-13/
- https://www.mozilla.org/security/advisories/mfsa2023-14/
- https://www.mozilla.org/security/advisories/mfsa2023-15/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1810191
