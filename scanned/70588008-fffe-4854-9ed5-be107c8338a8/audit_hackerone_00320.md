# [M] [domokeeper] Unintended Require

## Summary
Severity: Medium (CVSS 5.9)
Program: Node.js third-party modules
Weakness: Path Traversal
Reporter: ermilov
State: resolved
Disclosed: 2019-07-04T09:37:27.121Z
Source: https://hackerone.com/reports/538938

## Details
I would like to report Unintended Require vulnerability in `domokeeper`
It allows reading arbitary json files and load non-production code.

# Module

**module name:** domokeeper
**version:** 0.2.0
**npm page:** `https://www.npmjs.com/package/domokeeper`

## Module Description

domokeeper server: a pluggable domotic control server for Raspberry Pi 2/3

## Module Stats

[24] downloads in the last day
[45] downloads in the last week
[72] downloads in the last month

# Vulnerability

## Vulnerability Description

`domokeeper` is an express server which dynamically loads (with help of `require()`) some parts of the code. As long as the path to required module is passed in a HTTP request without any sanitization, anybody can cause code to load that was not intended to run on the server.

source code example:

index.js
line 83
```
app.get('/plugins/:id', function (req, res) {
  var plugin = require(req.params.id);
  res.json(plugin);
})
```

In addition, the fact that output of the module is passed to server response directly (in the example above) leads to an information leakage. For example it is possible to read `package.json` file or any other json file.


_Trimmed to 38 lines — full report: https://hackerone.com/reports/538938_
