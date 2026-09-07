# [C] [extra-asciinema] Command Injection via insecure command formatting

## Summary
Severity: Critical
Program: Node.js third-party modules
Weakness: Command Injection - Generic
Reporter: d3lla
State: resolved
Disclosed: 2020-08-22T08:48:20.138Z
Source: https://hackerone.com/reports/863956

## Details
I would like to report a `Command Injection` issue in the `extra-asciinema` module.
It allows to execute arbitrary commands on the victim's PC.

# Module

**module name:** `extra-asciinema`
**version:** `1.0.5`
**npm page:** `https://www.npmjs.com/package/extra-asciinema`

## Module Description

asciinema is a terminal screen recorder.

With this package you can auto-generate terminal recordings for Node.js examples through asciinema programmatically. Each method is also available as separate package for use by bundling tools, like browserify, rollup, uglify-js.

## Module Stats

[23] weekly downloads

# Vulnerability

## Vulnerability Description

The issue occurs because a user input parameter is used inside a command that is executed without any check. 

I tested the `uploadSync` function.
Here's the code which causes the issue:

```javascript
// https://github.com/nodef/extra-asciinema/blob/master/index.js#L214
...
const cp9 = require('child_process');
...
/**
 * Upload recorded asciicast to asciinema.org site.
 * @param {string} f filename
 * @returns {string} asciicast URL
 */
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/863956_
