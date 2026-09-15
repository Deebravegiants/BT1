# [H] CVE-2022-22751

## Summary
Severity: High
Advisory: CVE-2022-22751
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-12-22
Source: https://osv.dev/vulnerability/CVE-2022-22751
Type: osv

## Details
Mozilla developers Calixte Denizet, Kershaw Chang, Christian Holler, Jason Kratzer, Gabriele Svelto, Tyson Smith, Simon Giesecke, and Steve Fink reported memory safety bugs present in Firefox 95 and Firefox ESR 91.4. Some of these bugs showed evidence of memory corruption and we presume that with enough effort some of these could have been exploited to run arbitrary code. This vulnerability affects Firefox ESR < 91.5, Firefox < 96, and Thunderbird < 91.5.

## References
- https://www.mozilla.org/security/advisories/mfsa2022-01/
- https://www.mozilla.org/security/advisories/mfsa2022-02/
- https://www.mozilla.org/security/advisories/mfsa2022-03/
- https://bugzilla.mozilla.org/buglist.cgi?bug_id=1664149%2C1737816%2C1739366%2C1740274%2C1740797%2C1741201%2C1741869%2C1743221%2C1743515%2C1745373%2C1746011
