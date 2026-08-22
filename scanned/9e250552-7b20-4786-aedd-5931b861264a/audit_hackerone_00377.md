# [M] `concat-with-sourcemaps` allocates uninitialized Buffers when number is passed as a separator

## Summary
Severity: Medium (CVSS 6.5)
Program: Node.js third-party modules
Weakness: Out-of-bounds Read
Reporter: chalker
State: resolved
Disclosed: 2018-04-28T20:05:00.500Z
Source: https://hackerone.com/reports/320166

## Details
I would like to report an uninitialized Buffer allocation issue in `concat-with-sourcemaps`.
It allows to extract sensitive data from uninitialized memory or to cause a DoS by passing in a large number, in (unlikely) setups where `separator` is attacker-controlled.

# Module

**module name:** `concat-with-sourcemaps`
**version:** 1.0.5
**npm page:** `https://www.npmjs.com/package/concat-with-sourcemaps`

## Module Description

> NPM module for concatenating files and generating source maps.

## Module Stats

65 161 downloads in the last day
360 873 downloads in the last week
1 506 421 downloads in the last month

~18 077 052 estimated downloads per year

# Vulnerability

## Vulnerability Description

See https://github.com/floridoo/concat-with-sourcemaps/blob/master/index.js#L18

The problem arises when a number is passed as a separator. That is unlikely to be attacker-controlled in real-world setups, but not impossible. The API should not propagate the already-bad Buffer issue further.

On Node.js 6.x and below, this exposes uninitialized memory, which could contain sensitive data.

On all Node.js versions, this can cause a DoS when a big enough number (e.g. 1e8 or 1e9) is specified as a separator.

## Steps To Reproduce:

Uninitialized memory exposure (Node.js 6.x and below):

```
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/320166_
