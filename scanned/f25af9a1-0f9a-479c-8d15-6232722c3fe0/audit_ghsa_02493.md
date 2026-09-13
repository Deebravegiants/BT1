# [H] Arbitrary File Creation/Overwrite due to insufficient absolute path sanitization

## Summary
Severity: High
Advisory: GHSA-3jfq-g458-7qm9
CVE: CVE-2021-32804
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2021-08-03
Source: https://github.com/advisories/GHSA-3jfq-g458-7qm9
Type: github-advisory

## Affected
- npm: `tar` — affected >=0 <3.2.2
- npm: `tar` — affected >=4.0.0 <4.4.14
- npm: `tar` — affected >=5.0.0 <5.0.6
- npm: `tar` — affected >=6.0.0 <6.1.1

## Details
### Impact

Arbitrary File Creation, Arbitrary File Overwrite, Arbitrary Code Execution

`node-tar` aims to prevent extraction of absolute file paths by turning absolute paths into relative paths when the `preservePaths` flag is not set to `true`. This is achieved by stripping the absolute path root from any absolute file paths contained in a tar file. For example `/home/user/.bashrc` would turn into `home/user/.bashrc`. 

This logic was insufficient when file paths contained repeated path roots such as `////home/user/.bashrc`. `node-tar` would only strip a single path root from such paths. When given an absolute file path with repeating path roots, the resulting path (e.g. `///home/user/.bashrc`) would still resolve to an absolute path, thus allowing arbitrary file creation and overwrite. 

### Patches

3.2.2 || 4.4.14 || 5.0.6 || 6.1.1

NOTE: an adjacent issue [CVE-2021-32803](https://github.com/npm/node-tar/security/advisories/GHSA-r628-mhmh-qjhw) affects this release level. Please ensure you update to the latest patch levels that address CVE-2021-32803 as well if this adjacent issue affects your `node-tar` use case.

### Workarounds

Users may work around this vulnerability without upgrading by creating a custom `onentry` method which sanitizes the `entry.path` or a `filter` method which removes entries with absolute paths.

```js
const path = require('path')
const tar = require('tar')

tar.x({
  file: 'archive.tgz',
  // either add this function...
  onentry: (entry) => {
    if (path.isAbsolute(entry.path)) {
      entry.path = sanitizeAbsolutePathSomehow(entry.path)
      entry.absolute = path.resolve(entry.path)
    }
  },

  // or this one
  filter: (file, entry) => {
    if (path.isAbsolute(entry.path)) {
      return false
    } else {
      return true
    }
  }
})
```

Users are encouraged to upgrade to the latest patch versions, rather than attempt to sanitize tar input themselves.

## References
- https://github.com/npm/node-tar/security/advisories/GHSA-3jfq-g458-7qm9
- https://nvd.nist.gov/vuln/detail/CVE-2021-32804
- https://github.com/npm/node-tar/commit/1f036ca23f64a547bdd6c79c1a44bc62e8115da4
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
- https://github.com/npm/node-tar
- https://www.npmjs.com/advisories/1770
- https://www.npmjs.com/package/tar
- https://www.oracle.com/security-alerts/cpuoct2021.html
