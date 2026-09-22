# [M] CVE-2022-26386

## Summary
Severity: Medium
Advisory: CVE-2022-26386
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-26386
Type: osv

## Details
Previously Firefox for macOS and Linux would download temporary files to a user-specific directory in <code>/tmp</code>, but this behavior was changed to download them to <code>/tmp</code> where they could be affected by other local users. This behavior was reverted to the original, user-specific directory. <br>*This bug only affects Firefox for macOS and Linux. Other operating systems are unaffected.*. This vulnerability affects Firefox ESR < 91.7 and Thunderbird < 91.7.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-11/
- https://www.mozilla.org/security/advisories/mfsa2022-12/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1752396
