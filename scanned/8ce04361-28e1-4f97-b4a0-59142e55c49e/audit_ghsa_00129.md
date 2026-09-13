# [C] Command Injection in egg-scripts

## Summary
Severity: Critical
Advisory: GHSA-c9j3-wqph-5xx9
CVE: CVE-2018-3786
CWE: CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-09-17
Source: https://github.com/advisories/GHSA-c9j3-wqph-5xx9
Type: github-advisory

## Affected
- npm: `egg-scripts` — affected >=0 <2.8.1

## Details
Versions of `egg-scripts` before 2.8.1 are vulnerable to command injection. This is only exploitable if a malicious argument is provided on the command line.


Example:
`eggctl start --daemon --stderr='/tmp/eggctl_stderr.log; touch /tmp/malicious'`


## Recommendation

Update to version 2.8.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3786
- https://github.com/eggjs/egg-scripts/pull/26
- https://github.com/eggjs/egg-scripts/commit/b98fd03d1e3aaed68004b881f0b3d42fe47341dd
- https://hackerone.com/reports/388936
- https://github.com/advisories/GHSA-c9j3-wqph-5xx9
- https://github.com/eggjs/egg-scripts/blob/2.8.1/History.md
- https://www.npmjs.com/advisories/694
