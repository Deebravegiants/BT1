# [C] PIDUsage Enables OS Command Injection

## Summary
Severity: Critical
Advisory: GHSA-h2p3-h48h-9jj7
CVE: CVE-2017-1000220
CWE: CWE-78
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-h2p3-h48h-9jj7
Type: github-advisory

## Affected
- npm: `pidusage` — affected >=0 <1.1.5

## Details
### Overview
Affected versions of pidusage pass unsanitized input to `child_process.exec()`, resulting in arbitrary code execution in the `ps` method.

This package is vulnerable to this PoC on Darwin, SunOS, FreeBSD, and AIX.

Windows and Linux are not vulnerable.

### Proof of Concept
```js
var pid = require('pidusage');
pid.stat('1 && /usr/local/bin/python');
```

### Remediation
Update to version 1.1.5 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-1000220
- https://github.com/soyuka/pidusage/commit/b70eca15f7ca7f1b82a15f8a5d4bb48737f5a89d
- https://github.com/soyuka/pidusage
- https://web.archive.org/web/20201208183910/https://www.npmjs.com/advisories/356
