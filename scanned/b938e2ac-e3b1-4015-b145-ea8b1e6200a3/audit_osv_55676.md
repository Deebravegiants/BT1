# [C] CVE-2026-2792

## Summary
Severity: Critical
Advisory: CVE-2026-2792
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-02-24
Source: https://osv.dev/vulnerability/CVE-2026-2792
Type: osv

## Details
Memory safety bugs present in Firefox ESR 140.7, Thunderbird ESR 140.7, Firefox 147 and Thunderbird 147. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox < 148, Firefox ESR < 140.8, Thunderbird < 148, and Thunderbird < 140.8.

## References
- https://www.mozilla.org/security/advisories/mfsa2026-15/
- https://www.mozilla.org/security/advisories/mfsa2026-16/
- https://www.mozilla.org/security/advisories/mfsa2026-17/
- https://www.mozilla.org/security/advisories/mfsa2026-13/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=2008912%2C2010050%2C2010275%2C2012331
