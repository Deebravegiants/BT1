# [H] CVE-2022-46872

## Summary
Severity: High
Advisory: CVE-2022-46872
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-46872
Type: osv

## Details
An attacker who compromised a content process could have partially escaped the sandbox to read arbitrary files via clipboard-related IPC messages.<br>*This bug only affects Thunderbird for Linux. Other operating systems are unaffected.*. This vulnerability affects Firefox < 108, Firefox ESR < 102.6, and Thunderbird < 102.6.

## References
- https://security.gentoo.org/glsa/202305-06
- https://security.gentoo.org/glsa/202305-13
- https://www.mozilla.org/security/advisories/mfsa2022-51/
- https://www.mozilla.org/security/advisories/mfsa2022-52/
- https://www.mozilla.org/security/advisories/mfsa2022-53/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1799156
