# [M] Prototype Pollution in systeminformation

## Summary
Severity: Medium
Advisory: GHSA-4v2w-h9jm-mqjg
CVE: CVE-2020-26245
CWE: CWE-471, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2020-11-27
Source: https://github.com/advisories/GHSA-4v2w-h9jm-mqjg
Type: github-advisory

## Affected
- npm: `systeminformation` — affected >=0 <4.30.5

## Details
### Impact
command injection vulnerability by prototype pollution

### Patches
Problem was fixed with a rewrite of shell sanitations to avoid prototyper pollution problems. Please upgrade to version >= 4.30.2

### Workarounds
If you cannot upgrade, be sure to check or sanitize service parameter strings that are passed to si.inetChecksite()

### For more information
If you have any questions or comments about this advisory:

* Open an issue in [systeminformation](https://github.com/sebhildebrandt/systeminformation/issues/new?template=bug_report.md)

## References
- https://github.com/sebhildebrandt/systeminformation/security/advisories/GHSA-4v2w-h9jm-mqjg
- https://nvd.nist.gov/vuln/detail/CVE-2020-26245
- https://github.com/sebhildebrandt/systeminformation/commit/8113ff0e87b2f422a5756c48f1057575e73af016
