# [H] Command Injection Vulnerability in kill-port Package

## Summary
Severity: High (CVSS 7.3)
Program: Node.js third-party modules
Weakness: Command Injection - Generic
Reporter: cris_semmle
State: resolved
Disclosed: 2019-01-06T00:18:52.269Z
CVE: CVE-2019-5414
Source: https://hackerone.com/reports/389561

## Details
I would like to report a command injection vulnerability in kill-port. It allows an attacker to inject arbitrary commands. 

# Module

**module name:** kill-port
**version:** 1.3.1
**npm page:** `https://www.npmjs.com/package/kill-port`

## Module Description

 Kill the process running on given port

## Module Stats

5,282 downloads in the last week

# Vulnerability

## Vulnerability Description

If an attacker can control the port, which in itself is a very sensitive value, he can inject arbitrary OS commands due to the usage of exec in a third-party module.

## Steps To Reproduce:

```js
const kill = require('kill-port');
kill("23;`touch ./success.txt; 2222222222`");
```

## Patch

N/A replace exec (through execa.shell) with spawn

## Supporting Material/References:

# Wrap up

- I contacted the maintainer to let them know: N

_Trimmed to 38 lines — full report: https://hackerone.com/reports/389561_
