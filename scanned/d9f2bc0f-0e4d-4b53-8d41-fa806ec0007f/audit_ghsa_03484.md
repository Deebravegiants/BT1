# [H] Null characters not escaped

## Summary
Severity: High
Advisory: GHSA-f2rp-38vg-j3gh
CVE: CVE-2021-21384
CWE: CWE-88
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2021-03-18
Source: https://github.com/advisories/GHSA-f2rp-38vg-j3gh
Type: github-advisory

## Affected
- npm: `shescape` — affected >=0 <1.1.3

## Details
### Impact

Anyone using _Shescape_ to defend against shell injection may still be vulnerable against shell injection if the attacker manages to insert a [null character](https://en.wikipedia.org/wiki/Null_character) into the payload. For example (on Windows):

```javascript
const cp = require("child_process");
const shescape = require("shescape");

const nullChar = String.fromCharCode(0);
const payload = "foo\" && ls -al ${nullChar} && echo \"bar";
console.log(cp.execSync(`echo ${shescape.quote(payload)}`));
// foototal 3
// drwxr-xr-x 1 owner XXXXXX      0 Mar 13 18:44 .
// drwxr-xr-x 1 owner XXXXXX      0 Mar 13 00:09 ..
// drwxr-xr-x 1 owner XXXXXX      0 Mar 13 18:42 folder                                                                 
// -rw-r--r-- 1 owner XXXXXX      0 Mar 13 18:42 file
```

### Patches

The problem has been patched in [v1.1.3](https://github.com/ericcornelissen/shescape/releases/tag/v1.1.3) which you can upgrade to now. No further changes are required.

### Workarounds

Alternatively, null characters can be stripped out manually using e.g. `arg.replace(/\u{0}/gu, "")`

## References
- https://github.com/ericcornelissen/shescape/security/advisories/GHSA-f2rp-38vg-j3gh
- https://nvd.nist.gov/vuln/detail/CVE-2021-21384
- https://github.com/ericcornelissen/shescape/commit/07a069a66423809cbedd61d980c11ca44a29ea2b
- https://github.com/ericcornelissen/shescape/releases/tag/v1.1.3
- https://www.npmjs.com/package/shescape
