# [M] [harp] Path traversal using symlink

## Summary
Severity: Medium (CVSS 5.3)
Program: Node.js third-party modules
Weakness: Path Traversal
Reporter: skyn3t
State: resolved
Disclosed: 2019-04-09T09:28:48.626Z
CVE: CVE-2019-5438
Source: https://hackerone.com/reports/530289

## Details
In reference to #453820

# Module

**module name:** harp
**version:** 0.29.0
**npm page:** `https://www.npmjs.com/package/harp`

## Module Description

zero-configuration web server with built in pre-processing

## Module Stats

2,679 downloads in the last week

# Vulnerability
Path traversal using symlink.

## Vulnerability Description

Similar to #403703. It can be used to list any file in another folder of web root.

## Steps To Reproduce

- Install harpjs

```
yarn global add harp
```

- Run harp server

```
harp server
```

- Create a symlink inside your project directory.

_Trimmed to 38 lines — full report: https://hackerone.com/reports/530289_
