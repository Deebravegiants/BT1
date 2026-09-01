# [M] `protobufjs` is vulnerable to ReDoS when parsing crafted invalid *.proto files

## Summary
Severity: Medium (CVSS 4.5)
Program: Node.js third-party modules
Weakness: Uncontrolled Resource Consumption
Reporter: chalker
State: resolved
Disclosed: 2018-03-31T20:38:42.297Z
CVE: CVE-2018-3738
Source: https://hackerone.com/reports/319576

## Details
I would like to report a ReDoS in `protobufjs`
It allows to cause Denial of Service by trying to parse (or load) a crafted `*.proto` file.

# Module

**module name:** protobufjs
**version:** 6.8.5
**npm page:** `https://www.npmjs.com/package/[MODULE NAME]`

## Module Description

> Protocol Buffers are a language-neutral, platform-neutral, extensible way of serializing structured data for use in communications protocols, data storage, and more, originally designed at Google (see).

## Module Stats

-22 592 downloads in the last day
352 974 downloads in the last week
1 321 151 downloads in the last month

~15 853 812 estimated downloads per year

# Vulnerability

## Vulnerability Description

ReDoS.
- regex: `/^(?:\.?[a-zA-Z_][a-zA-Z_0-9]*)+$/`
- evil string: `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx!`
- file: https://github.com/dcodeIO/protobuf.js/blob/6.8.5/src/parse.js#L27 

## Steps To Reproduce:

proto file:

```
// awesome.proto
package awesomepackage;
syntax = "proto3";
```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/319576_
