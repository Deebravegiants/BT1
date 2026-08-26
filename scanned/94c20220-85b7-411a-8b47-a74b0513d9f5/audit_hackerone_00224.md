# [C] [vboxmanage.js] Command Injection via insecure command concatenation

## Summary
Severity: Critical
Program: Node.js third-party modules
Weakness: Command Injection - Generic
Reporter: d3lla
State: resolved
Disclosed: 2020-08-20T09:08:23.411Z
Source: https://hackerone.com/reports/864777

## Details
I would like to report a `Command Injection` issue in the `vboxmanage.js` module.
It allows to execute arbitrary commands on the victim's PC.

# Module

**module name:** `vboxmanage.js`
**version:** `1.0.6`
**npm page:** `https://www.npmjs.com/package/vboxmanage.js`

## Module Description

A wrapper for VirtualBox CLI with Promises,

## Module Stats

[2] weekly downloads

# Vulnerability

## Vulnerability Description

The issue occurs because a user input parameter is used inside a command that is executed without any check. 

I tested the `start` function.
Here's the code which causes the issue:

```javascript
// https://github.com/danielgindi/node-vboxmanage/blob/master/index.js#L76
...
var
    child_process = require('child_process'),
...
VBoxManage.manage = function (command, options) {

    command = command || [];
    if (!(command instanceof Array)) {
        command = [command];
    }
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/864777_
