# [C] Command Injection Vulnerability in find-exec

## Summary
Severity: Critical
Advisory: GHSA-95rp-6gqp-6622
CVE: CVE-2023-40582
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-08-30
Source: https://github.com/advisories/GHSA-95rp-6gqp-6622
Type: github-advisory

## Affected
- npm: `find-exec` — affected >=0 <1.0.3

## Details
Older versions of the package are vulnerable to Command Injection as an attacker controlled parameter. As a result, attackers may run malicious commands.

For example:

```
const find = require("find-exec");
find("mplayer; touch hacked")
```

This creates a file named "hacked" on the filesystem.

You should never allow users to control commands to find, since this package attempts to run every command provided.

Thanks to @miguelafmonteiro for reporting.

## References
- https://github.com/shime/find-exec/security/advisories/GHSA-95rp-6gqp-6622
- https://nvd.nist.gov/vuln/detail/CVE-2023-40582
- https://github.com/shime/find-exec/commit/74fb108097c229b03d6dba4cce81e36aa364b51c
- https://github.com/shime/find-exec
