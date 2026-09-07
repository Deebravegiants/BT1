# [M] Exposure of home directory through shescape on Unix with Bash

## Summary
Severity: Medium
Advisory: GHSA-446w-rrm4-r47f
CVE: CVE-2022-24725
CWE: CWE-200, CWE-78
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-03-03
Source: https://github.com/advisories/GHSA-446w-rrm4-r47f
Type: github-advisory

## Affected
- npm: `shescape` — affected >=1.4.0 <1.5.1

## Details
### Impact

The issue allows for exposure of the home directory on Unix systems when using Bash with the `escape` or `escapeAll` functions from the _shescape_ API with the `interpolation` option set to `true`. Other tested shells, Dash and Zsh, are not affected.

```javascript
const cp = require("child_process");
const shescape = require("shescape");

const payload = "home_directory=~";
const options = { interpolation: true };
console.log(cp.execSync(`echo ${shescape.escape(payload, options)}`));
// home_directory=/home/user
```

Depending on how the output of _shescape_ is used, directory traversal may be possible in the application using _shescape_.

### Patches

The issue was patched in `v1.5.1`.

### Workarounds

Manually escape all instances of the tilde character (`~`) using `arg.replace(/~/g, "\\~")`.

### References

See GitHub issue https://github.com/ericcornelissen/shescape/issues/169.

## References
- https://github.com/ericcornelissen/shescape/security/advisories/GHSA-446w-rrm4-r47f
- https://nvd.nist.gov/vuln/detail/CVE-2022-24725
- https://github.com/ericcornelissen/shescape/issues/169
- https://github.com/ericcornelissen/shescape/pull/170
- https://github.com/ericcornelissen/shescape
