# [H] Velocity.js has a Prototype Pollution vulnerability through #set path assignment

## Summary
Severity: High
Advisory: GHSA-j658-c2gf-x6pq
CVE: CVE-2026-44966
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:L (CVSS_V3)
Published: 2026-05-09
Source: https://github.com/advisories/GHSA-j658-c2gf-x6pq
Type: github-advisory

## Affected
- npm: `velocityjs` — affected >=0

## Details
### Summary
A prototype pollution vulnerability was discovered in Velocity.js <= 2.1.5. This issue occurs during the processing of #set directives in Velocity templates. If an application renders a template controlled by an attacker, it is possible to modify Object.prototype, potentially leading to Denial of Service (DoS) or Remote Code Execution (RCE) depending on the server environment.

### Details
The root cause is located in the #set path assignment logic within the source code:
- File: /src/compile/set.ts 
- Issue: The engine accepts arbitrary path keys and performs assignments using the logic `(baseRef as Record<string, unknown>)[key] = val`.


Because there is no validation or filtering to block sensitive keys such as \_\_proto\_\_, constructor, or prototype, an attacker can traverse the prototype chain and pollute the global Object.prototype.

### PoC
```javascript
const {render} = require('velocityjs');
delete Object.prototype.polluted;
console.log({}.polluted); // ""
render('#set($__proto__.polluted = "hacked")', {});
console.log({}.polluted); // "hacked"
delete Object.prototype.polluted;
```

### Impact
- Vulnerability Type: Prototype Pollution
- Who is impacted: Any application that renders Velocity templates where the template content can be influenced or controlled by untrusted users.
- Severity: High. Prototype pollution can often be used to bypass security controls, cause application crashes (DoS), or be chained with other vulnerabilities to achieve code execution.

## References
- https://github.com/shepherdwind/velocity.js/security/advisories/GHSA-j658-c2gf-x6pq
- https://nvd.nist.gov/vuln/detail/CVE-2026-44966
- https://github.com/shepherdwind/velocity.js
