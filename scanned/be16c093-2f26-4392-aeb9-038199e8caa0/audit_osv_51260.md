# [H] CVE-2021-23964

## Summary
Severity: High
Advisory: CVE-2021-23964
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-02-26
Source: https://osv.dev/vulnerability/CVE-2021-23964
Type: osv

## Details
Mozilla developers reported memory safety bugs present in Firefox 84 and Firefox ESR 78.6. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox < 85, Thunderbird < 78.7, and Firefox ESR < 78.7.

## References
- https://www.mozilla.org/security/advisories/mfsa2021-03/
- https://www.mozilla.org/security/advisories/mfsa2021-04/
- https://www.mozilla.org/security/advisories/mfsa2021-05/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1662507%2C1666285%2C1673526%2C1674278%2C1674835%2C1675097%2C1675844%2C1675868%2C1677590%2C1677888%2C1680410%2C1681268%2C1682068%2C1682938%2C1683736%2C1685260%2C1685925
