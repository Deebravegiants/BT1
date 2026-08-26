# [C] `memjs` allocates and stores buffers on typed input, resulting in DoS and uninitialized memory usage

## Summary
Severity: Critical (CVSS 10.0)
Program: Node.js third-party modules
Weakness: Uncontrolled Resource Consumption
Reporter: chalker
State: resolved
Disclosed: 2018-06-27T05:25:55.386Z
CVE: CVE-2018-3767
Source: https://hackerone.com/reports/319809

## Details
I would like to report a Buffer allocation vulnerability in `memjs`.

In cases when the attacker is able to pass typed input (e.g. via JSON) to the storage, it allows to cause DoS (on all Node.js versions) and to store (and potentially later extract) chunks of uninitialized server memory containing sensitive data.

# Module

**module name:** `memjs`
**version:** 1.1.0
**npm page:** `https://www.npmjs.com/package/memjs`

## Module Description

> MemJS is a pure Node.js client library for using memcache, in particular, the MemCachier service. It uses the binary protocol and support SASL authentication.

## Module Stats

186 downloads in the last day
2 903 downloads in the last week
12 037 downloads in the last month

~144 444 estimated downloads per year *(yay, a pretty number)*

# Vulnerability

## Vulnerability Description

`memjs` passes `value` option to the Buffer constructor without proper sanitization, resulting in DoS and uninitialized memory leak in setups where an attacker could submit typed input to the 'value' parameter (e.g. JSON).

## Steps To Reproduce:

`memcached` should be up and running.

### DoS

```js
var client = require('memjs').Client.create()
function tick() {
  var value = 2e9;
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/319809_
