# [M] Command Injection Vulnerability in systeminformation

## Summary
Severity: Medium
Advisory: GHSA-m57p-p67h-mq74
CVE: CVE-2020-26274
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-12-16
Source: https://github.com/advisories/GHSA-m57p-p67h-mq74
Type: github-advisory

## Affected
- npm: `systeminformation` — affected >=0 <4.31.1

## Details
### Impact
command injection vulnerability

### Patches
Problem was fixed with a shell string sanitation fix. Please upgrade to version >= 4.31.1

### Workarounds
If you cannot upgrade, be sure to check or sanitize service parameter strings that are passed to si.inetLatency()

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [systeminformation](https://github.com/sebhildebrandt/systeminformation/issues/new?template=bug_report.md)

## References
- https://github.com/sebhildebrandt/systeminformation/security/advisories/GHSA-m57p-p67h-mq74
- https://nvd.nist.gov/vuln/detail/CVE-2020-26274
- https://github.com/sebhildebrandt/systeminformation/commit/1faadcbf68f1b1fdd5eb2054f68fc932be32ac99
- https://www.npmjs.com/advisories/1590
- https://www.npmjs.com/package/systeminformation
