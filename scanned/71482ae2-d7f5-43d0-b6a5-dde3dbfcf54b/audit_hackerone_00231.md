# [M] Fastify uses allErrors: true ajv configuration by default which is susceptible to DoS

## Summary
Severity: Medium (CVSS 5.3)
Program: Node.js third-party modules
Weakness: Uncontrolled Resource Consumption
Reporter: chalker
State: resolved
Disclosed: 2020-07-29T12:53:44.132Z
CVE: CVE-2020-8192
Source: https://hackerone.com/reports/903521

## Details
I would like to report a denial of service vulnerability in fastify
It allows to cause a DoS with some schemas that were otherwise assumed to be secure against DoS by their authors

# Module

**module name:** fastify
**version:** `2.14.1`, `3.0.0-rc.4`
**npm page:** `https://www.npmjs.com/package/fastify`

## Module Description

> An efficient server implies a lower cost of the infrastructure, a better responsiveness under load and happy users. 

## Module Stats

114 076 weekly downloads

# Vulnerability

## Vulnerability Description

See <https://github.com/ajv-validator/ajv#security-risks-of-trusted-schemas>:

> **Please note:** The suggestions above to prevent slow validation would only work if you do NOT use `allErrors: true` in production code (using it would continue validation after validation errors).

`fastify` uses `allErrors: true` by default which makes it susceptible to DoS attacks even when schemas are otherwise safe.

E.g. a (sub-)schema `{ uniqueItems: true, maxItems: 10 }` is otherwise safe against DoS as `maxItems` is checked **first** and validation fails there on long arrays, _but that applies to only not in `allErrors: true` case_. 

Neither https://github.com/fastify/fastify/blob/master/docs/Validation-and-Serialization.md nor https://github.com/fastify/fastify/blob/master/docs/Recommendations.md mentions this directly.

Introduced in https://github.com/fastify/fastify/pull/1398

## Steps To Reproduce:

```js
/* Client */

```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/903521_
