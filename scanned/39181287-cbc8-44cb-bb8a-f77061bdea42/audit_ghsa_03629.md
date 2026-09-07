# [M] Pomelo allows external control of critical state data

## Summary
Severity: Medium
Advisory: GHSA-4x6v-rwh4-55jw
CVE: CVE-2019-18954
CWE: CWE-668
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2019-12-02
Source: https://github.com/advisories/GHSA-4x6v-rwh4-55jw
Type: github-advisory

## Affected
- npm: `pomelo` — affected >=0 <2.2.7

## Details
Pomelo v2.2.5 allows external control of critical state data. A malicious user input can corrupt arbitrary methods and attributes in `template/game-server/app/servers/connector/handler/entryHandler.js` because certain internal attributes can be overwritten via a conflicting name. Hence, a malicious attacker can manipulate internal attributes by adding additional attributes to user input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-18954
- https://github.com/NetEase/pomelo/issues/1149
- https://github.com/cl0udz/vulnerabilities/tree/master/pomelo-critical-state-manipulation
