# [H] LiquidJS: Root restriction bypass for partial and layout loading through symlinked templates

## Summary
Severity: High
Advisory: GHSA-56p5-8mhr-2fph
CVE: CVE-2026-35525
CWE: CWE-61
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-56p5-8mhr-2fph
Type: github-advisory

## Affected
- npm: `liquidjs` — affected >=0 <10.25.3

## Details
### Summary

LiquidJS enforces partial and layout root restrictions using the resolved pathname string, but it does not resolve the canonical filesystem path before opening the file. A symlink placed inside an allowed partials or layouts directory can therefore point to a file outside that directory and still be loaded.

### Details

For `{% include %}`, `{% render %}`, and `{% layout %}`, LiquidJS checks whether the candidate path is inside the configured partials or layouts roots before reading it. That check is path-based, not realpath-based.

Because of that, a file like `partials/link.liquid` passes the directory containment check as long as its pathname is under the allowed root. If `link.liquid` is actually a symlink to a file outside the allowed root, the filesystem follows the symlink when the file is opened and LiquidJS renders the external target.

So the restriction is applied to the path string that was requested, not to the file that is actually read.

This matters in environments where an attacker can place templates or otherwise influence files under a trusted template root, including uploaded themes, extracted archives, mounted content, or repository-controlled template trees.

### PoC

```js
const { Liquid } = require('liquidjs');
const fs = require('fs');

fs.rmSync('/tmp/liquid-root', { recursive: true, force: true });
fs.mkdirSync('/tmp/liquid-root', { recursive: true });

fs.writeFileSync('/tmp/secret-outside.liquid', 'SECRET_OUTSIDE');
fs.symlinkSync('/tmp/secret-outside.liquid', '/tmp/liquid-root/link.liquid');

const engine = new Liquid({ root: ['/tmp/liquid-root'] });

engine.parseAndRender('{% render "link.liquid" %}')
  .then(console.log);
// SECRET_OUTSIDE
```

### Impact

If an attacker can place or influence symlinks under a trusted partials or layouts directory, they can make LiquidJS read and render files outside the intended template root. In practice this can expose arbitrary readable files reachable through symlink targets.

## References
- https://github.com/harttle/liquidjs/security/advisories/GHSA-56p5-8mhr-2fph
- https://nvd.nist.gov/vuln/detail/CVE-2026-35525
- https://github.com/harttle/liquidjs/pull/867
- https://github.com/harttle/liquidjs
- https://github.com/harttle/liquidjs/releases/tag/v10.25.3
