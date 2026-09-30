# [H] content-security-policy-parser Prototype Pollution Vulnerability May Lead to RCE

## Summary
Severity: High
Advisory: GHSA-w2cq-g8g3-gm83
CVE: CVE-2025-55164
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-08-12
Source: https://github.com/advisories/GHSA-w2cq-g8g3-gm83
Type: github-advisory

## Affected
- npm: `content-security-policy-parser` — affected >=0 <0.6.0

## Details
### Impact
A prototype pollution vulnerability exists in versions 0.5.0 and earlier, wherein if you provide a policy name called `__proto__` you can override the Object prototype.

For example:

```
const parse = require('content-security-policy-parser');

const x = parse("default-src 'self'; __proto__ foobar");
console.log('raw print:', x);
console.log('toString:', x.toString());
```

Outputs:

```
raw print: Array { 'default-src': [ "'self'" ] }
toString: foobar
```

Whilst no gadget exists in this library, it is possible via other libraries expose functionality that enable RCE. It is customary to label prototype pollution vulnerabilities in this way. The most common effect of this is denial of service, as you can trivially overwrite properties.

As the content security policy is provided in HTTP queries, it is incredibly likely that network exploitation is possible.

### Patches
There has been a patch implemented a year ago (11 Feb 2024), but low uptake of patched versions has not been observed in the wild - only 17% of weekly downloads are of patched versions.

### Workarounds
By disabling prototype method in NodeJS you can neutralise all possible prototype pollution attacks. Provide either `--disable-proto=delete` (recommended) or `--disable-proto=throw` as an argument to `node` to enable this feature.

### References
[Issue revealing the problem, January 26 2024](https://github.com/helmetjs/content-security-policy-parser/issues/11)
[Commit fixing the problem](https://github.com/helmetjs/content-security-policy-parser/commit/b13a52554f0168af393e3e38ed4a94e9e6aea9dc)

Credit to @EvanHahn for patching the vulnerability promptly, and @pnappa (Patrick Nappa) for discovery.

## References
- https://github.com/helmetjs/content-security-policy-parser/security/advisories/GHSA-w2cq-g8g3-gm83
- https://nvd.nist.gov/vuln/detail/CVE-2025-55164
- https://github.com/helmetjs/content-security-policy-parser/issues/11
- https://github.com/helmetjs/content-security-policy-parser/commit/b13a52554f0168af393e3e38ed4a94e9e6aea9dc
- https://github.com/helmetjs/content-security-policy-parser
