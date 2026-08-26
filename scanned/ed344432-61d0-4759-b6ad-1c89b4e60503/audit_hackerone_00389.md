# [H] Path Traversal on Resolve-Path

## Summary
Severity: High (CVSS 8.6)
Program: Node.js third-party modules
Weakness: Path Traversal
Reporter: orange
State: resolved
Disclosed: 2018-02-22T21:20:52.170Z
CVE: CVE-2018-3732
Source: https://hackerone.com/reports/315760

## Details
The author of `resolve-path` told me that I can submit this to here. The vulnerability already reported to the author and got a fixed!

## Module

**module name:** resolve-path
**version:** 1.3.3
**npm page:** `https://www.npmjs.com/package/resolve-path`

### Description

Resolve a relative path against a root path with validation.

This module would protect against commons attacks like GET /../file.js which reaches outside the root folder.

### Module Stats

Stats
[8264] downloads in the last day
[48226] downloads in the last week
[210556] downloads in the last month

~[2526672] estimated downloads per year

## Description

The library failed to process path like `C:../../` on Windows

## Steps To Reproduce:

```js
require('resolve-path')("C:/windows/temp/", "C:../../")
```

## Supporting Material/References:

- Windows 10
- Node v8.9.4
- NPM 5.6.0

_Trimmed to 38 lines — full report: https://hackerone.com/reports/315760_
