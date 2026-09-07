# [M] LiquidJS's `{% render %}` tag silently bypasses per-render `ownPropertyOnly:true` via `Context.spawn()`

## Summary
Severity: Medium
Advisory: GHSA-9x9p-qf8f-mvjg
CVE: CVE-2026-44646
CWE: CWE-693
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-9x9p-qf8f-mvjg
Type: github-advisory

## Affected
- npm: `liquidjs` — affected >=0

## Details
## Summary

`Context.spawn()` in liquidjs creates a child `Context` for the `{% render %}` tag but does not propagate the parent context's resolved `ownPropertyOnly` value. The new context re-derives `ownPropertyOnly` from `opts.ownPropertyOnly` (the instance-level option), silently discarding any `RenderOptions.ownPropertyOnly` override that was supplied to `parseAndRender()`. As a result, a developer who runs a Liquid instance with the backwards-compatible `ownPropertyOnly:false` and then locks down an untrusted render with `parseAndRender(..., { ownPropertyOnly: true })` still leaks prototype-chain properties from inside any `{% render %}` partial. This is a distinct exploit surface from the previously identified array-filter variants (`where`, `reject`, `group_by`, `find`, `find_index`, `has`) — the underlying root cause in `Context.spawn()` is shared, but `{% render %}` is a separately reachable sink that needs no filter usage.

## Details

The bug is in `Context.spawn()`:

```ts
// src/context/context.ts:105-114
public spawn (scope = {}) {
  return new Context(scope, this.opts, {
    sync: this.sync,
    globals: this.globals,
    strictVariables: this.strictVariables
    // <-- ownPropertyOnly is missing here
  }, {
    renderLimit: this.renderLimit,
    memoryLimit: this.memoryLimit
  })
}
```

The constructor resolves `ownPropertyOnly` as:

```ts
// src/context/context.ts:47
this.ownPropertyOnly = renderOptions.ownPropertyOnly ?? opts.ownPropertyOnly
```

Because `spawn()` passes a `RenderOptions` object with no `ownPropertyOnly`, the child context falls back to `opts.ownPropertyOnly` (the instance-level option), throwing away any per-render override that the parent context had applied. `this.opts` is the raw normalized instance options object; it is not mutated to reflect render-time overrides.

The `{% render %}` tag at `src/tags/render.ts:51-77` calls `spawn()` to build the partial's isolated scope:

```ts
* render (ctx: Context, emitter: Emitter): Generator<unknown, void, unknown> {
  const { liquid, hash } = this
  const filepath = (yield renderFilePath(this['file'], ctx, liquid)) as string
  assert(filepath, () => `illegal file path "${filepath}"`)

  const childCtx = ctx.spawn()                    // <-- ownPropertyOnly lost here
  const scope = childCtx.bottom()
  __assign(scope, yield hash.render(ctx))
  ...
  const templates = (yield liquid._parsePartialFile(filepath, childCtx.sync, this['currentFile'])) as Template[]
  yield liquid.renderer.renderTemplates(templates, childCtx, emitter)
}
```

All template variable lookups inside the partial then go through `childCtx.readProperty()` (`src/context/context.ts:123-135`), which calls `readJSProperty(obj, key, this.ownPropertyOnly)`. With `childCtx.ownPropertyOnly === false` (inherited from `opts`), the protective check at `src/context/context.ts:138-141` is skipped and prototype-chain properties are returned to the template:

```ts
export function readJSProperty (obj: Scope, key: PropertyKey, ownPropertyOnly: boolean) {
  if (ownPropertyOnly && !hasOwnProperty.call(obj, key) && !(obj instanceof Drop)) return undefined
  return obj[key]
}
```

The `{% include %}` tag is **not** affected: it does not call `spawn()`; it pushes onto the parent context's scope stack (`src/tags/include.ts:40`), so the parent's resolved `ownPropertyOnly` continues to apply.

Trust model / why this matters: `RenderOptions.ownPropertyOnly` is documented (`src/liquid-options.ts:108-111`) as "Same as `ownPropertyOnly` on LiquidOptions, but only for current `render()` call". It exists precisely so that developers running a non-strict instance can lock down individual untrusted renders. That contract is broken — the override is silently dropped at every partial boundary.

## PoC

```bash
mkdir -p /tmp/render-poc
printf '{{ user.passwordHash }}' > /tmp/render-poc/_user.liquid

node -e "
const { Liquid } = require('./dist/liquid.node.js');
const liquid = new Liquid({ ownPropertyOnly: false, root: '/tmp/render-poc' });

class User { constructor(n){ this.name = n; } }
User.prototype.passwordHash = 'bcrypt\$secret';
const u = new User('alice');

liquid.parseAndRender(
  'Direct:[{{ user.passwordHash }}] Render:[{% render \"_user.liquid\", user: user %}]',
  { user: u },
  { ownPropertyOnly: true }
).then(console.log);
"
```

Verified output on liquidjs 10.25.7:

```
Direct:[] Render:[bcrypt$secret]
```

The top-level expression `{{ user.passwordHash }}` is correctly blocked by the per-render `ownPropertyOnly:true`, but the same expression inside the partial loaded by `{% render %}` returns the prototype-chain property — proof that `Context.spawn()` discarded the override.

## Impact

- **Information disclosure**: Any prototype-chain property of objects passed into a `{% render %}` partial — including secrets, hashes, internal state, framework-injected helpers — becomes readable from inside the partial template, even when the developer used the documented per-render lockdown.
- **Realistic threat model**: Applications that maintain `ownPropertyOnly:false` for backwards compatibility (or because their data layer relies on prototype methods) and lock down untrusted-template renders with `parseAndRender(..., { ownPropertyOnly:true })` are protected at the top level but silently exposed inside any partial. User-controllable template content (CMS snippets, theme partials, email templates) that uses `{% render %}` becomes an info-leak primitive.
- **Distinct from existing CVE-2022-25948**: the prior advisory only covered direct use of `ownPropertyOnly:false`; this is a failure of the documented mitigation (`ownPropertyOnly:true` per-render override), not a missing setting.
- **Distinct from the array-filter variant**: same `spawn()` root cause, but exploitable without invoking `where/reject/group_by/find/find_index/has` — only requires that the template uses `{% render %}` (a basic templating feature) and that one of the rendered values has prototype-chain properties.

## Recommended Fix

Propagate `ownPropertyOnly` (and any other security-relevant render options) inside `Context.spawn()`:

```ts
// src/context/context.ts
public spawn (scope = {}) {
  return new Context(scope, this.opts, {
    sync: this.sync,
    globals: this.globals,
    strictVariables: this.strictVariables,
    ownPropertyOnly: this.ownPropertyOnly   // <-- propagate resolved per-render value
  }, {
    renderLimit: this.renderLimit,
    memoryLimit: this.memoryLimit
  })
}
```

Passing `this.ownPropertyOnly` (the resolved value, not `this.opts.ownPropertyOnly`) ensures any `RenderOptions.ownPropertyOnly` override flows into spawned child contexts. This single change closes both the `{% render %}` pathway documented here and the array-filter pathway tracked separately. A regression test should assert that a partial rendered via `{% render %}` honours `parseAndRender(..., { ownPropertyOnly: true })` against an object with prototype-chain properties.

## References
- https://github.com/harttle/liquidjs/security/advisories/GHSA-9x9p-qf8f-mvjg
- https://nvd.nist.gov/vuln/detail/CVE-2026-44646
- https://github.com/harttle/liquidjs/commit/dbbf6288030591bf6da28d8c1cce5a17bca97bb6
- https://github.com/harttle/liquidjs
- https://github.com/harttle/liquidjs/releases/tag/v10.26.0
