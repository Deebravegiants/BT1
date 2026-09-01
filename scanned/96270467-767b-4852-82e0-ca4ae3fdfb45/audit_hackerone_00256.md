# [C] Prototype pollution in multipart parsing

## Summary
Severity: Critical (CVSS 9.3)
Program: Node.js third-party modules
Weakness: Uncontrolled Resource Consumption
Reporter: mcollina
State: resolved
Disclosed: 2020-02-28T10:55:15.010Z
CVE: CVE-2020-8136
Source: https://hackerone.com/reports/804772

## Details
I would like to report a prototype pollution attack in fastify-multipart it allows to crash a remote server parsing multipart requests by sending a specially crafted request.

# Module

**module name:** fastify-multipart
**version:** all versions before < v1.0.5. v1.0.5 contains the fix. 
**npm page:** `https://www.npmjs.com/package/fastify-multipart`

## Module Description

[Fastify](https://www.fastify.io) plugin to parse the multipart content-type.

Under the hood it uses [busboy](http://npm.im/busboy).

## Module Stats

weekly downloads: 4900

# Vulnerability

## Vulnerability Description

Eran Hammer found this vulnerability for Hapi, he tested Fastify as well and found it vulnerable.
Here is the Hapi vulnerability report: https://www.npmjs.com/advisories/1479. 

## Steps To Reproduce:

> Detailed steps to reproduce with all required references/steps/commands. If there is any exploit code or reference to the package source code this is the place where it should be put.

## Patch

This was already released in https://github.com/fastify/fastify-multipart/pull/116 and version 1.0.5 issued.

# Wrap up

> Select Y or N for the following statements:

- I contacted the maintainer to let them know: Y

_Trimmed to 38 lines — full report: https://hackerone.com/reports/804772_
