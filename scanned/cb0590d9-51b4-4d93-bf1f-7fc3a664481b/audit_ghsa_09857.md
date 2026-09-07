# [M] Hono: Path traversal in toSSG() allows writing files outside the output directory

## Summary
Severity: Medium
Advisory: GHSA-xf4j-xp2r-rqqx
CVE: CVE-2026-39408
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:L/AC:H/AT:P/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-xf4j-xp2r-rqqx
Type: github-advisory

## Affected
- npm: `hono` — affected >=4.0.0 <4.12.12

## Details
## Summary

A path traversal issue in `toSSG()` allows files to be written outside the configured output directory during static site generation. When using dynamic route parameters via `ssgParams`, specially crafted values can cause generated file paths to escape the intended output directory.

## Details

The static site generation process creates output files based on route paths derived from application routes and parameters. When `ssgParams` is used to provide values for dynamic routes, those values are used to construct output file paths. If these values contain traversal sequences (e.g. `..`), the resulting output path may resolve outside the configured output directory. As a result, files may be written to unintended locations instead of being confined within the specified output directory.

For example:
 
```ts
import { Hono } from 'hono'
import { toSSG, ssgParams } from 'hono/ssg'

const app = new Hono()

app.get('/:id', ssgParams([{ id: '../pwned' }]), (c) => {
  return c.text('pwned')
})

toSSG(app, fs, { dir: './static' })
```

In this case, the generated output path may resolve outside `./static`, resulting in a file being written outside the intended output directory.

## Impact

An attacker who can influence values passed to `ssgParams` during the build process may be able to write files outside the intended output directory.

Depending on the build and deployment environment, this may:

* overwrite unintended files
* affect generated artifacts
* impact deployment outputs or downstream tooling

This issue is limited to build-time static site generation and does not affect request-time routing.

## References
- https://github.com/honojs/hono/security/advisories/GHSA-xf4j-xp2r-rqqx
- https://nvd.nist.gov/vuln/detail/CVE-2026-39408
- https://github.com/honojs/hono/commit/b470278920fffcfd6d76002755d6db53db827679
- https://github.com/honojs/hono
- https://github.com/honojs/hono/releases/tag/v4.12.12
