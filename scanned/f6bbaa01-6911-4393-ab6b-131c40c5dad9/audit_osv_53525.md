# [H] CVE-2022-46881

## Summary
Severity: High
Advisory: CVE-2022-46881
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-46881
Type: osv

## Details
An optimization in WebGL was incorrect in some cases, and could have led to memory corruption and a potentially exploitable crash.
*Note*: This advisory was added on December 13th, 2022 after we better understood the impact of the issue. The fix was included in the original release of Firefox 106. This vulnerability affects Firefox < 106, Firefox ESR < 102.6, and Thunderbird < 102.6.

## References
- https://security.gentoo.org/glsa/202305-06
- https://security.gentoo.org/glsa/202305-13
- https://www.mozilla.org/security/advisories/mfsa2022-44/
- https://www.mozilla.org/security/advisories/mfsa2022-52/
- https://www.mozilla.org/security/advisories/mfsa2022-53/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1770930
