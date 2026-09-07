# [M] [freespace] Command Injection due to Lack of Sanitization

## Summary
Severity: Medium
Program: Node.js third-party modules
Weakness: Command Injection - Generic
Reporter: ansuj7
State: resolved
Disclosed: 2020-10-14T15:50:41.478Z
Source: https://hackerone.com/reports/951249

## Details
I would like to report `Command Injection` in the `freespace` module.
It allows an attacker to inject and execute shell commands on Unix based systems.

# Module

**module name:** freespace
**version:** 1.0.4
**npm page:** `https://www.npmjs.com/package/freespace`

## Module Description

A library that tells you how much free disk space you have.  
- Works on all platform.
- No dependencies and no native libraries.

## Module Stats

[26] weekly downloads

# Vulnerability

## Vulnerability Description

The library offers a function that allows a developer to pass in a disk-label (Windows) or a mount-point (Linux) and returns space details about the same. However, due to lack of proper sanitization of the parameter to that function, injection of multiple commands using delimiters such as `;` and `&&` will cause the shell to interpret and execute each command between those characters.  
This code is vulnerable on the Unix platform and not on Windows. The Windows variant also directly uses the input without sanitization, however, uses only the first character of the input parameter, which prevents injection.

This is the vulnerable code in `index.js` of the library:
```javascript
exports.check = function(driveOrMount, callback) {
    return new Promise(function(resolve, reject) {
        let cb = function(err, stdout, stderr) { ... };
        if (!driveOrMountRegex.test(driveOrMount)) {
            let err = new Error(DRIVE_STRING_ERROR);
            if (callback) callback(err);
            return reject(err);
        }
        if (process.platform === 'win32') {
            driveOrMount = driveOrMount.charAt(0).toLowerCase();
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/951249_
