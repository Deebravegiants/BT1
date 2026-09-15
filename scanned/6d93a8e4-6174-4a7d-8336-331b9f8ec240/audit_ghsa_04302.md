# [M] UAParser.js: Unbounded `Sec-CH-UA-Model` parsing can trigger ReDoS in `withClientHints()`

## Summary
Severity: Medium
Advisory: GHSA-9h5v-pfqq-x599
CVE: CVE-2026-48125
CWE: CWE-1333, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-9h5v-pfqq-x599
Type: github-advisory

## Affected
- npm: `ua-parser-js` — affected >=2.0.1 <2.0.10

## Details
### Summary

A regular expression denial-of-service (ReDoS) vulnerability has been discovered in `ua-parser-js` when using the Client Hints API. By sending a crafted `Sec-CH-UA-Model` header to an application that calls `UAParser(headers).withClientHints()`, an attacker can cause the parser to spend excessive CPU time due to catastrophic backtracking in the device [regex](https://github.com/faisalman/ua-parser-js/blob/2.0.9/src/main/ua-parser.js#L615):

```js
/ ([\w ]+) miui\/v?\d/i
```

Unlike when using the `User-Agent` value, which has a hard limit of `UA_MAX_LENGTH = 500`, when using Client Hints, values are copied without a length limit before being passed into regex parsing.

### PoC

```js
const { UAParser } = require('ua-parser-js');

const headers = {
  'sec-ch-ua-platform': '"Android"',
  'sec-ch-ua-mobile': '?1',
  'sec-ch-ua-model': '"' + 'A '.repeat(25000) + '"'
};

const t0 = process.hrtime.bigint();
UAParser(headers).withClientHints();
const ms = Number(process.hrtime.bigint() - t0) / 1e6;

if (ms > 100) {
  console.log('Potential ReDoS');
}
```

### Impact

This vulnerability allows an unauthenticated attacker to trigger a denial-of-service condition in any __server-side__ application that uses `UAParser(headers).withClientHints()`. A single request with a ~32,000-character model value can consume over 400ms of CPU time, with parsing time growing polynomially with input length. The impact is __availability__ only, there is no confidentiality or integrity impact.

### Affected Versions

`ua-parser-js` versions `>=2.0.1, <=2.0.9` are affected. The `withClientHints()` API is not present in version `0.7.x` or `1.x`.

### Patches

A patch has been released to fix the vulnerable regular expression and limit the Client Hints input. Users should update to version `2.0.10` or later.

### References

- [Regular expression Denial of Service - ReDoS (OWASP)](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS)

### Credits

Thanks to [@sondt99](https://github.com/sondt99), who first reported the issue.

## References
- https://github.com/faisalman/ua-parser-js/security/advisories/GHSA-9h5v-pfqq-x599
- https://github.com/faisalman/ua-parser-js
