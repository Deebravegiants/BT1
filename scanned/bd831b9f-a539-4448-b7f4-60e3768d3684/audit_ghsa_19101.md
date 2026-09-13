# [H] eazy-logger prototype pollution

## Summary
Severity: High
Advisory: GHSA-r7jx-5m6m-cpg9
CVE: CVE-2024-57075
CWE: CWE-1321, CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-02-06
Source: https://github.com/advisories/GHSA-r7jx-5m6m-cpg9
Type: github-advisory

## Affected
- npm: `eazy-logger` — affected >=0 <4.1.0

## Details
A prototype pollution in the lib.Logger function of eazy-logger v4.0.1 allows attackers to cause a Denial of Service (DoS) via supplying a crafted payload.

An attacker can supply a payload with `Object.prototype` setter to introduce or modify properties within the global prototype chain, causing denial of service (DoS) a the minimum consequence.

Moreover, the consequences of this vulnerability can escalate to other injection-based attacks, depending on how the library integrates within the application. For instance, if the polluted property propagates to sensitive Node.js APIs (e.g., `child_process.exec`, `eval`), it could enable an attacker to execute arbitrary commands within the application's context.

## Proof of Concept

```js
(async () => {
const lib = await import('eazy-logger');
var someObj = {}
console.log("Before Attack: ", JSON.stringify({}.__proto__));
try {
// for multiple functions, uncomment only one for each execution.
lib.Logger (JSON.parse('{"__proto__":{"pollutedKey":123}}'))
} catch (e) { }
console.log("After Attack: ", JSON.stringify({}.__proto__));
delete Object.prototype.pollutedKey;
})();
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-57075
- https://github.com/shakyShane/eazy-logger/commit/a8baa6fe441d19ffa9916eba367016b7937a28fd
- https://gist.github.com/tariqhawis/c601f7f85146510ca899a7406a03aba5
- https://github.com/shakyShane/eazy-logger
