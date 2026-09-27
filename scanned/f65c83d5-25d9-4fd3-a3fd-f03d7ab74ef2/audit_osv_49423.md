# [H] CVE-2019-11759

## Summary
Severity: High
Advisory: CVE-2019-11759
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-01-08
Source: https://osv.dev/vulnerability/CVE-2019-11759
Type: osv

## Details
An attacker could have caused 4 bytes of HMAC output to be written past the end of a buffer stored on the stack. This could be used by an attacker to execute arbitrary code or more likely lead to a crash. This vulnerability affects Firefox < 70, Thunderbird < 68.2, and Firefox ESR < 68.2.

## References
- https://www.mozilla.org/security/advisories/mfsa2019-33/
- https://www.mozilla.org/security/advisories/mfsa2019-34/
- https://www.mozilla.org/security/advisories/mfsa2019-35/
- https://security.gentoo.org/glsa/202003-10
- https://usn.ubuntu.com/4335-1/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1577953
