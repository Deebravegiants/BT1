# [C] `whereis` concatenates unsanitized input into exec() command

## Summary
Severity: Critical (CVSS 9.9)
Program: Node.js third-party modules
Weakness: Command Injection - Generic
Reporter: chalker
State: resolved
Disclosed: 2018-03-28T06:17:58.607Z
CVE: CVE-2018-3772
Source: https://hackerone.com/reports/319476

## Details
I would like to report command injection in `whereis`
It allows to inject arbitrary shell commands by trying to locate crafted filenames.

# Module

**module name:** whereis
**version:** 0.4.0
**npm page:** `https://www.npmjs.com/package/whereis`

## Module Description

> Simply get the first path to a bin on any system.

## Module Stats

Stats
101 downloads in the last day
5 403 downloads in the last week
18 945 downloads in the last month

~227 340 estimated downloads per year [JUST FOR REFERENCE,  ~DOWNLOADS PER MONTH*12]

# Vulnerability

## Vulnerability Description

File name argument is not properly escaped before being concatenated into the command that is passed to `exec()`.

See lines https://github.com/vvo/node-whereis/blob/master/index.js#L4-L12

## Steps To Reproduce:

```js
var whereis = require('whereis');
var filename = 'wget; touch /tmp/tada';
whereis(filename, function(err, path) {
  console.log(path);
});
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/319476_
