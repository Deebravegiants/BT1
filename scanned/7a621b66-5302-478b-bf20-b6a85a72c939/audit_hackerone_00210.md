# [M] [@knutkirkhorn/free-space] - Command Injection through Lack of Sanitization

## Summary
Severity: Medium (CVSS 6.8)
Program: Node.js third-party modules
Weakness: Command Injection - Generic
Reporter: ansuj7
State: resolved
Disclosed: 2020-09-18T12:35:51.099Z
Source: https://hackerone.com/reports/950192

## Details
I would like to report ```Command Injection``` in the ```free-space``` module.
It allows ```arbitrary shell command execution on Unix-based systems```

# Module

**module name:** ```free-space```
**version:** ```1.2.0```
**npm page:** `https://www.npmjs.com/package/free-space`

## Module Description

 Get the amount of free space for a drive

## Module Stats

24 Weekly Downloads

# Vulnerability

## Vulnerability Description

The issue is triggered due to the lack of sanitization of the input parameter of the library's exported anonymous function. 
The exported function, when given a parameter checks what platform the code is being run on and sends that parameter to a function call in either ```lib/unix.js``` or ```lib/windows/js```.
The vulnerability exists in ```lib/unix.js``` which directly uses the user-input parameter: ```disk``` in the template string that ultimately gets exec-ed.

Below is the library's ```index.js``:

```javascript
'use strict';
const systemDisk = require('system-disk');
const windows = require('./lib/windows.js');
const unix = require('./lib/unix.js');

module.exports = disk => {
    if (disk === undefined) {
        return new Promise(resolve => {
            systemDisk().then(newDisk => {
                disk = newDisk;
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/950192_
