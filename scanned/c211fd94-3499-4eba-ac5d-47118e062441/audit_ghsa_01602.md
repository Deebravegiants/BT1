# [M] Command Injection in systeminformation

## Summary
Severity: Medium
Advisory: GHSA-fj59-f6c3-3vw4
CVE: CVE-2020-26300
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2020-10-27
Source: https://github.com/advisories/GHSA-fj59-f6c3-3vw4
Type: github-advisory

## Affected
- npm: `systeminformation` — affected >=0 <4.26.2

## Details
### Impact
command injection vulnerability

### Patches
Problem was fixed with a shell string sanitation fix. Please upgrade to version >= 4.26.2

### Workarounds
If you cannot upgrade, be sure to check or sanitize service parameter strings that are passed to `is.services()`, `is.inetChecksite()`, `si.inetLatency()`, `si.networkStats()`, `is.services()` and `si.processLoad()`

### References
_Are there any links users can visit to find out more?_

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [systeminformation](https://github.com/sebhildebrandt/systeminformation)

## References
- https://github.com/sebhildebrandt/systeminformation/security/advisories/GHSA-fj59-f6c3-3vw4
- https://nvd.nist.gov/vuln/detail/CVE-2020-26300
- https://github.com/sebhildebrandt/systeminformation/commit/bad372e654cdd549e7d786acbba0035ded54c607
- https://github.com/advisories/GHSA-fj59-f6c3-3vw4
- https://github.com/sebhildebrandt/systeminformation
- https://www.npmjs.com/package/systeminformation
