# [C] Prototype pollution in aurelia-path

## Summary
Severity: Critical
Advisory: GHSA-3c9c-2p65-qvwv
CVE: CVE-2021-41097
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-09-27
Source: https://github.com/advisories/GHSA-3c9c-2p65-qvwv
Type: github-advisory

## Affected
- npm: `aurelia-path` — affected >=0 <1.1.7

## Details
### Impact
The vulnerability exposes Aurelia application that uses `aurelia-path` package to parse a string. The majority of this will be Aurelia applications that employ the `aurelia-router` package. An example is this could allow an attacker to change the prototype of base object class `Object` by tricking an application to parse the following URL: `https://aurelia.io/blog/?__proto__[asdf]=asdf`

### Patches
The problem should be patched in version `1.1.7`. Any version earlier than this is vulnerable.

### Workarounds
A partial work around is to free the Object prototype:
```ts
Object.freeze(Object.prototype)
```

## References
- https://github.com/aurelia/path/security/advisories/GHSA-3c9c-2p65-qvwv
- https://nvd.nist.gov/vuln/detail/CVE-2021-41097
- https://github.com/aurelia/path/issues/44
- https://github.com/aurelia/path/commit/7c4e235433a4a2df9acc313fbe891758084fdec1
- https://github.com/aurelia/path
- https://github.com/aurelia/path/releases/tag/1.1.7
- https://www.npmjs.com/package/aurelia-path
