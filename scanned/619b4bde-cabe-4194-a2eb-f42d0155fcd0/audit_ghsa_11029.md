# [M] Unhead has XSS bypass in `useHeadSafe` via attribute name injection and case-sensitive protocol check

## Summary
Severity: Medium
Advisory: GHSA-g5xx-pwrp-g3fv
CVE: CVE-2026-31860
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-g5xx-pwrp-g3fv
Type: github-advisory

## Affected
- npm: `unhead` — affected >=0 <2.1.11

## Details
## Summary

`useHeadSafe()` can be bypassed to inject arbitrary HTML attributes, including event handlers, into SSR-rendered `<head>` tags. This is the composable that Nuxt docs recommend for safely handling user-generated content.

## Details

**XSS via `data-*` attribute name injection**

The `acceptDataAttrs` function (safe.ts, line 16-20) allows any property key starting with `data-` through to the final HTML. It only checks the prefix, not whether the key contains spaces or other characters that break HTML attribute parsing.

```typescript
function acceptDataAttrs(value: Record<string, string>) {
  return Object.fromEntries(
    Object.entries(value || {}).filter(([key]) => key === 'id' || key.startsWith('data-')),
  )
}
```

This result gets merged into every tag's props at line 114:

```typescript
tag.props = { ...acceptDataAttrs(prev), ...next }
```

Then `propsToString` (propsToString.ts, line 26) interpolates property keys directly into the HTML string with no sanitization:

```typescript
attrs += value === true ? ` ${key}` : ` ${key}="${encodeAttribute(value)}"`
```

A space in the key breaks out of the attribute name. Everything after the space becomes separate HTML attributes.

### PoC

The most practical vector uses a `link` tag. `<link rel="stylesheet">` fires `onload` once the stylesheet loads, giving reliable script execution:

```javascript
useHeadSafe({
  link: [{
    rel: 'stylesheet',
    href: '/valid-stylesheet.css',
    'data-x onload=alert(document.domain) y': 'z'
  }]
})
```

SSR output:

```html
<link data-x onload=alert(document.domain) y="z" rel="stylesheet" href="/valid-stylesheet.css">
```

The browser parses `onload=alert(document.domain)` as its own attribute. Once the stylesheet loads, the handler fires.

The same injection works on any tag type since `acceptDataAttrs` is applied to all of them at line 114. Here's the same thing on a `meta` tag (the injected attributes render, though `onclick` doesn't fire on non-interactive `<meta>` elements):

```javascript
useHeadSafe({
  meta: [{
    name: 'description',
    content: 'legitimate content',
    'data-x onclick=alert(document.domain) y': 'z'
  }]
})
```

### Realistic scenario

A Nuxt app accepts SEO metadata from a CMS or user profile. The developer uses `useHeadSafe()` as the docs recommend. An attacker puts a `data-*` key with spaces and an event handler into their input. The payload renders into the HTML on every page load.

## Suggested fix

For vulnerability 1, validate that attribute names only contain characters legal in HTML attributes:

```typescript
const SAFE_ATTR_RE = /^[a-zA-Z][a-zA-Z0-9\-]*$/

function acceptDataAttrs(value: Record<string, string>) {
  return Object.fromEntries(
    Object.entries(value || {}).filter(
      ([key]) => (key === 'id' || key.startsWith('data-')) && SAFE_ATTR_RE.test(key)
    ),
  )
}
```

## References
- https://github.com/unjs/unhead/security/advisories/GHSA-g5xx-pwrp-g3fv
- https://nvd.nist.gov/vuln/detail/CVE-2026-31860
- https://github.com/unjs/unhead/commit/9ecc4f9568b0e23938f36d4b23fcfa4a18a89045
- https://github.com/unjs/unhead
- https://github.com/unjs/unhead/releases/tag/v2.1.11
