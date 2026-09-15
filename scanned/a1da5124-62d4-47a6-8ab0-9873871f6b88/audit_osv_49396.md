# [H] CVE-2019-11707

## Summary
Severity: High
Advisory: CVE-2019-11707
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-07-23
Source: https://osv.dev/vulnerability/CVE-2019-11707
Type: osv

## Details
A type confusion vulnerability can occur when manipulating JavaScript objects due to issues in Array.pop. This can allow for an exploitable crash. We are aware of targeted attacks in the wild abusing this flaw. This vulnerability affects Firefox ESR < 60.7.1, Firefox < 67.0.3, and Thunderbird < 60.7.2.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2019-11707
- https://security.gentoo.org/glsa/201908-12
- https://www.mozilla.org/security/advisories/mfsa2019-18/
- https://www.mozilla.org/security/advisories/mfsa2019-20/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1544386
