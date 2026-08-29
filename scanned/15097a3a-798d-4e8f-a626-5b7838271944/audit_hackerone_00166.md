# [C] [wireguard-wrapper] Command Injection via insecure command concatenation

## Summary
Severity: Critical
Program: Node.js third-party modules
Weakness: Command Injection - Generic
Reporter: d3lla
State: resolved
Disclosed: 2021-04-16T21:23:42.350Z
Source: https://hackerone.com/reports/858674

## Details
I would like to report a `Command Injection` issue in the `wireguard-wrapper` module.
It allows to execute arbitrary commands on the victim's PC.

# Module

**module name:** `wireguard-wrapper`
**version:** `1.0.2`
**npm page:** `https://www.npmjs.com/package/wireguard-wrapper`

## Module Description

This project is a nodejs wrapper for the wireguard commands wg and wg-quick.

Features:
- No dependencies
- Uses promises

Limitations:
- So far it can only read but not write anything
- missing wg set, wg setconf, wg addconf, wg syncconf

## Module Stats

[0] weekly downloads

# Vulnerability

## Vulnerability Description

The issue occurs because a user input parameter is used inside a command that is executed without any check. 

I tested the `wg showconf` functionality. 
Here's the code which causes the issue:

```javascript
// https://github.com/rostwolke/node-wireguard-wrapper/blob/master/src/command/Wg.js#L58
'use strict';
const {exec} = require('child_process');
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/858674_
