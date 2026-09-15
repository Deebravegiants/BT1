# [M] Tmp files readable by other users in sync-exec

## Summary
Severity: Medium
Advisory: GHSA-38h8-x697-gh8q
CVE: CVE-2017-16024
CWE: CWE-377
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2018-11-09
Source: https://github.com/advisories/GHSA-38h8-x697-gh8q
Type: github-advisory

## Affected
- npm: `sync-exec` — affected >=0

## Details
Affected versions of `sync-exec` use files located in `/tmp/` to buffer command results before returning values. As `/tmp/` is almost always set with world readable permissions, this may allow low privilege users on the system to read the results of commands run via `sync-exec` under a higher privilege user.


## Recommendation

There is currently no direct patch for `sync-exec`, as the `child_process.execSync` function provided in Node.js v0.12.0 and later provides the same functionality natively. 

The best mitigation currently is to update to Node.js v0.12.0 or later, and migrate all uses of `sync-exec` to `child_process.execSync()`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-16024
- https://github.com/gvarsanyi/sync-exec/issues/17
- https://cwe.mitre.org/data/definitions/377.html
- https://github.com/advisories/GHSA-38h8-x697-gh8q
- https://www.npmjs.com/advisories/310
- https://www.owasp.org/index.php/Insecure_Temporary_File
