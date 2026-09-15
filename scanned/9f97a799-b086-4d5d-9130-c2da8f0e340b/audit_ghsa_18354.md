# [C] CodeceptJS's incomprehensive sanitation can lead to Command Injection

## Summary
Severity: Critical
Advisory: GHSA-34w8-mcwr-vg29
CVE: CVE-2025-57285
CWE: CWE-77
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-09-08
Source: https://github.com/advisories/GHSA-34w8-mcwr-vg29
Type: github-advisory

## Affected
- npm: `codeceptjs` — affected >=3.5.0 <3.7.5

## Details
CodeceptJS versions 3.5.0 through 3.7.5-beta.18 contain a command injection vulnerability in the emptyFolder function (lib/utils.js). The execSync command directly concatenates the user-controlled directoryPath parameter without sanitization or escaping, allowing attackers to execute arbitrary commands.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-57285
- https://github.com/codeceptjs/CodeceptJS/pull/3604
- https://github.com/codeceptjs/CodeceptJS/pull/5190
- https://gist.github.com/Dremig/1ba111f9b1f7cffe1fcb4838b64e55b9
- https://github.com/codeceptjs/CodeceptJS
- https://www.npmjs.com
