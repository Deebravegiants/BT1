# [H] CVE-2019-17026

## Summary
Severity: High
Advisory: CVE-2019-17026
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-03-02
Source: https://osv.dev/vulnerability/CVE-2019-17026
Type: osv

## Details
Incorrect alias information in IonMonkey JIT compiler for setting array elements could lead to a type confusion. We are aware of targeted attacks in the wild abusing this flaw. This vulnerability affects Firefox ESR < 68.4.1, Thunderbird < 68.4.1, and Firefox < 72.0.1.

## References
- https://www.cisa.gov/known-exploited-vulnerabilities-catalog?field_cve=CVE-2019-17026
- https://security.gentoo.org/glsa/202003-02
- https://usn.ubuntu.com/4335-1/
- https://www.mozilla.org/security/advisories/mfsa2020-03/
- https://www.mozilla.org/security/advisories/mfsa2020-04/
- https://bugzilla.mozilla.org/show_bug.cgi?id=1607443
- http://packetstormsecurity.com/files/162568/Firefox-72-IonMonkey-JIT-Type-Confusion.html
