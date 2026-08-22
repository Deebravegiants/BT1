# [C] [extra-ffmpeg] Command Injection via insecure command formatting

## Summary
Severity: Critical
Program: Node.js third-party modules
Weakness: Command Injection - Generic
Reporter: d3lla
State: resolved
Disclosed: 2020-08-20T09:08:41.263Z
Source: https://hackerone.com/reports/863944

## Details
I would like to report a `Command Injection` issue in the `extra-ffmpeg` module.
It allows to execute arbitrary commands on the victim's PC.

# Module

**module name:** `extra-ffmpeg`
**version:** `4.0.3`
**npm page:** `https://www.npmjs.com/package/extra-ffmpeg`

## Module Description

Decode, encode, transcode, mux, demux, stream, filter, and play media through machine (via "ffmpeg").

## Module Stats

[99] weekly downloads

# Vulnerability

## Vulnerability Description

The issue occurs because a user input parameter is used inside a command that is executed without any check. 

Here's the code which causes the issue:

```javascript
// https://github.com/nodef/extra-ffmpeg/blob/master/index.js#L19
const cp = require('child_process');


// Global variables.
const STDIO = [0, 1, 2];


 // Generate command for ffmpeg.
 function command(os) {
  var z = 'ffmpeg';
  var os = os||[];
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/863944_
