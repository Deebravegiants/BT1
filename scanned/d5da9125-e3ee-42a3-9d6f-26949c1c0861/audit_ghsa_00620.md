# [H] Prototype Pollution in hoek

## Summary
Severity: High
Advisory: GHSA-jp4x-w63m-7wgm
CVE: CVE-2018-3728
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-04-26
Source: https://github.com/advisories/GHSA-jp4x-w63m-7wgm
Type: github-advisory

## Affected
- npm: `hoek` — affected >=5.0.0 <5.0.3
- npm: `hoek` — affected >=0 <4.2.1

## Details
Versions of `hoek` prior to 4.2.1 and 5.0.3 are vulnerable to prototype pollution.

The `merge` function, and the `applyToDefaults` and `applyToDefaultsWithShallow` functions which leverage `merge` behind the scenes, are vulnerable to a prototype pollution attack when provided an _unvalidated_ payload created from a JSON string containing the `__proto__` property.

This can be demonstrated like so:

```javascript
var Hoek = require('hoek');
var malicious_payload = '{"__proto__":{"oops":"It works !"}}';

var a = {};
console.log("Before : " + a.oops);
Hoek.merge({}, JSON.parse(malicious_payload));
console.log("After : " + a.oops);
```

This type of attack can be used to overwrite existing properties causing a potential denial of service.


## Recommendation

Update to version 4.2.1, 5.0.3 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-3728
- https://github.com/hapijs/hoek/commit/32ed5c9413321fbc37da5ca81a7cbab693786dee
- https://github.com/hapijs/hoek/commit/5aed1a8c4a3d55722d1c799f2368857bf418d6df
- https://hackerone.com/reports/310439
- https://access.redhat.com/errata/RHSA-2018:1263
- https://access.redhat.com/errata/RHSA-2018:1264
- https://github.com/hapijs/hoek
- https://snyk.io/vuln/npm:hoek:20180212
- https://web.archive.org/web/20200227131737/https://www.securityfocus.com/bid/103108
