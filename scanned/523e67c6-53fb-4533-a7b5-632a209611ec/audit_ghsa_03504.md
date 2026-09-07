# [M] Remote code execution via the `pretty` option.

## Summary
Severity: Medium
Advisory: GHSA-p493-635q-r6gr
CVE: CVE-2021-21353
CWE: CWE-74, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2021-03-03
Source: https://github.com/advisories/GHSA-p493-635q-r6gr
Type: github-advisory

## Affected
- npm: `pug` — affected >=0 <3.0.1
- npm: `pug-code-gen` — affected >=0 <2.0.3
- npm: `pug-code-gen` — affected >=3.0.0 <3.0.2

## Details
### Impact

If a remote attacker was able to control the `pretty` option of the pug compiler, e.g. if you spread a user provided object such as the query parameters of a request into the pug template inputs, it was possible for them to achieve remote code execution on the node.js backend.

### Patches

Upgrade to `pug@3.0.1` or `pug-code-gen@3.0.2` or `pug-code-gen@2.0.3`, which correctly sanitise the parameter.

### Workarounds

If there is no way for un-trusted input to be passed to pug as the `pretty` option, e.g. if you compile templates in advance before applying user input to them, you do not need to upgrade.

### References


Original report: https://github.com/pugjs/pug/issues/3312

### For more information

If you believe you have found other vulnerabilities, please **DO NOT** open an issue. Instead, you can follow the instructions in our [Security Policy](https://github.com/pugjs/pug/blob/master/SECURITY.md)

## References
- https://github.com/pugjs/pug/security/advisories/GHSA-p493-635q-r6gr
- https://nvd.nist.gov/vuln/detail/CVE-2021-21353
- https://github.com/pugjs/pug/issues/3312
- https://github.com/pugjs/pug/pull/3314
- https://github.com/pugjs/pug/commit/991e78f7c4220b2f8da042877c6f0ef5a4683be0
- https://github.com/pugjs/pug/releases/tag/pug%403.0.1
- https://www.npmjs.com/package/pug
- https://www.npmjs.com/package/pug-code-gen
