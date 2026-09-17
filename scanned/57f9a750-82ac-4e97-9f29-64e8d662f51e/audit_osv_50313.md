# [H] CVE-2020-12387

## Summary
Severity: High
Advisory: CVE-2020-12387
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-05-26
Source: https://osv.dev/vulnerability/CVE-2020-12387
Type: osv

## Details
A race condition when running shutdown code for Web Worker led to a use-after-free vulnerability. This resulted in a potentially exploitable crash. This vulnerability affects Firefox ESR < 68.8, Firefox < 76, and Thunderbird < 68.8.0.

## References
- https://usn.ubuntu.com/4373-1/
- https://security.gentoo.org/glsa/202005-03
- https://security.gentoo.org/glsa/202005-04
- https://www.mozilla.org/security/advisories/mfsa2020-16/
- https://www.mozilla.org/security/advisories/mfsa2020-17/
- https://www.mozilla.org/security/advisories/mfsa2020-18/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1545345
