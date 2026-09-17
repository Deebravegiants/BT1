# [H] liquidjs has a path traversal fallback vulnerability

## Summary
Severity: High
Advisory: GHSA-wmfp-5q7x-987x
CVE: CVE-2026-30952
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-10
Source: https://github.com/advisories/GHSA-wmfp-5q7x-987x
Type: github-advisory

## Affected
- npm: `liquidjs` — affected >=0 <10.25.0

## Details
### Impact
The `layout`, `render`, and `include` tags allow arbitrary file access via absolute paths (either as string literals or through Liquid variables, the latter require `dynamicPartials: true`, which is the default). This poses a security risk when malicious users are allowed to control the template content or specify the filepath to be included as a Liquid variable.

### Patches
The root cause is LiquidJS allows `require.resolve()` as fallback but doesn't limit the directories it can resolve to. The issue is fixed via [#855](https://github.com/harttle/liquidjs/pull/855) and published version 10.25.0 on npm.

### Workarounds
#### Change the files in build time
In build time, through Shell script or Webpack `string-replace-loader`, change the file content of correxponding file (depending on your package `type`, for CommonJS it's `dist/liquid.node.js`) under `dist/`, 

```diff
  if (fs.fallback !== undefined) {
    const filepath = fs.fallback(file)
-   if (filepath !== undefined) yield filepath
+   if (filepath !== undefined) {
+     for (const dir of dirs) {
+       if (!enforceRoot || this.contains(dir, filepath)) {
+         yield filepath
+         break
+       }
+     }
    }
  }
```

#### Overriding by `fs` LiquidJS option
Adding a [`fs` option](https://liquidjs.com/api/interfaces/FS.html) to override the [default `fs` implementation](https://github.com/harttle/liquidjs/blob/1b85fdaa9c535021f7030a239a64003af26d31b5/src/fs/fs-impl.ts#L36-L40):

```javascript
const { statSync, readFileSync, promises: { stat, readFile } } = require('fs')
const { resolve, extname, dirname, sep } = require('path')

const fs = {
    exists: async (fp) => { try { await stat(fp); return true; } catch { return false } },
    existsSync: (fp) => { try { statSync(fp); return true } catch { return false } },
    resolve: (root, file, ext) => resolve(root, file + (extname(file) ? '' : ext)),
    contains: (root, file) => {
        const r = resolve(root)
        return file.startsWith(r.endsWith(sep) ? r : r + sep)
    },
    readFile: (fp) => readFile(fp, 'utf8'),
    readFileSync: (fp) => readFileSync(fp, 'utf8'),
    fallback: () => undefined,
    dirname,
    sep
};

const engine = new Liquid({ fs })
```

### References
Discussions: https://github.com/harttle/liquidjs/pull/851
Code fix: https://github.com/harttle/liquidjs/pull/855

## References
- https://github.com/harttle/liquidjs/security/advisories/GHSA-wmfp-5q7x-987x
- https://nvd.nist.gov/vuln/detail/CVE-2026-30952
- https://github.com/harttle/liquidjs/pull/851
- https://github.com/harttle/liquidjs/pull/855
- https://github.com/harttle/liquidjs/commit/3cd024d652dc883c46307581e979fe32302adbac
- https://github.com/harttle/liquidjs
