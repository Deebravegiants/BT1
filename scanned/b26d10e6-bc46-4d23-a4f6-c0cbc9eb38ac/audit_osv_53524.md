# [M] CVE-2022-46880

## Summary
Severity: Medium
Advisory: CVE-2022-46880
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-46880
Type: osv

## Details
A missing check related to tex units could have led to a use-after-free and potentially exploitable crash.<br />*Note*: This advisory was added on December 13th, 2022 after we better understood the impact of the issue. The fix was included in the original release of Firefox 105. This vulnerability affects Firefox ESR < 102.6, Firefox < 105, and Thunderbird < 102.6.

## References
- https://security.gentoo.org/glsa/202305-06
- https://security.gentoo.org/glsa/202305-13
- https://www.mozilla.org/security/advisories/mfsa2022-40/
- https://www.mozilla.org/security/advisories/mfsa2022-52/
- https://www.mozilla.org/security/advisories/mfsa2022-53/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1749292
