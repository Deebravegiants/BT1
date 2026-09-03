# [H] `foreman` is vulnerable to ReDoS in path

## Summary
Severity: High (CVSS 7.5)
Program: Node.js third-party modules
Weakness: Uncontrolled Resource Consumption
Reporter: chalker
State: resolved
Disclosed: 2018-04-28T20:31:32.910Z
Source: https://hackerone.com/reports/320586

## Details
I would like to report ReDoS in `foreman`.
It allows to cause denial of service by suppling a crafted path.

# Module

**module name:** foreman
**version:** 2.0.0
**npm page:** `https://www.npmjs.com/package/foreman`

## Module Description

> Node Foreman is a Node.js version of the popular Foreman tool, with a few Node specific changes.

## Module Stats

5 296 downloads in the last day
30 879 downloads in the last week
141 342 downloads in the last month

~1 696 104 estimated downloads per year

# Vulnerability

## Vulnerability Description

ReDoS.

Regex: `/http:\/\/[^/]*:?[0-9]*(\/.*)$/`
Evil string: `http://${Array(81000).join('0')}` (unwrap js template)
Line: https://github.com/strongloop/node-foreman/blob/v2.0.0/forward.js#L30
Blocks for ~5 seconds per request.

## Steps To Reproduce:

`nf start -f 9999`

```js
const net = require('net');
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/320586_
