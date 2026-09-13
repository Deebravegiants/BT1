# [H] CVE-2021-23978

## Summary
Severity: High
Advisory: CVE-2021-23978
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-02-26
Source: https://osv.dev/vulnerability/CVE-2021-23978
Type: osv

## Details
Mozilla developers reported memory safety bugs present in Firefox 85 and Firefox ESR 78.7. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox < 86, Thunderbird < 78.8, and Firefox ESR < 78.8.

## References
- https://www.mozilla.org/security/advisories/mfsa2021-07/
- https://www.mozilla.org/security/advisories/mfsa2021-08/
- https://www.mozilla.org/security/advisories/mfsa2021-09/
- https://lists.debian.org/debian-lts-announce/2021/03/msg00000.html
- https://security.gentoo.org/glsa/202104-09
- https://security.gentoo.org/glsa/202104-10
- https://www.debian.org/security/2021/dsa-4866
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=786797%2C1682928%2C1687391%2C1687597
