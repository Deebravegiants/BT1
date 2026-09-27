# [M] DOMPurify: Hook mutation of `data.allowedTags` / `data.allowedAttributes` permanently pollutes `DEFAULT_ALLOWED_TAGS` / `DEFAULT_ALLOWED_ATTR`

## Summary
Severity: Medium
Advisory: GHSA-76mc-f452-cxcm
CVE: CVE-2026-65902
CWE: CWE-501, CWE-693
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-76mc-f452-cxcm
Type: github-advisory

## Affected
- npm: `dompurify` — affected >=0 <3.4.7

## Details
# Hook mutation of `data.allowedTags` / `data.allowedAttributes` permanently pollutes `DEFAULT_ALLOWED_TAGS` / `DEFAULT_ALLOWED_ATTR`

**CWE**: CWE-501 (Trust Boundary Violation — hook-scoped mutation leaks to global default sets) via CWE-693 (Protection Mechanism Failure — the default allow-list is silently widened for all subsequent sanitize calls)

## Summary

The `data.allowedTags` and `data.allowedAttributes` fields passed to `uponSanitizeElement` and `uponSanitizeAttribute` hooks are **direct references** to the library's live `ALLOWED_TAGS` / `ALLOWED_ATTR` sets. For sanitize calls that don't supply an explicit `cfg.ALLOWED_TAGS` / `cfg.ALLOWED_ATTR` array, those live sets are themselves direct references to the module-level `DEFAULT_ALLOWED_TAGS` / `DEFAULT_ALLOWED_ATTR` constants. A hook that mutates these fields — a natural-looking pattern for "allow `X` for this iteration" — permanently writes new entries into the default constants for the DOMPurify instance's lifetime. Every subsequent sanitize call that doesn't override the config inherits the widened defaults, so an attacker payload that uses the poisoned tag/attribute name survives sanitization. `removeAllHooks()`, `clearConfig()`, and even passing a fresh `cfg: {}` do not recover; only constructing a new DOMPurify instance does.

The maintainer's existing defense at `src/purify.ts:696-700` explicitly clones `DEFAULT_ALLOWED_TAGS` before mutating it via `cfg.ADD_TAGS` (array form), demonstrating awareness of this exact class. The hook path remained uncovered.

## Affected

- DOMPurify ≤ 3.4.5, including `main` at `7996f1dc78eb8b7922388aed75d94a9f8fad9a36`
- Any application that installs a hook on `uponSanitizeElement` or `uponSanitizeAttribute` that writes to `data.allowedTags[...] = true` or `data.allowedAttributes[...] = true` and later sanitizes attacker-influenced content with default config (no explicit `cfg.ALLOWED_TAGS` / `cfg.ALLOWED_ATTR` array)

## Vulnerability details

### [A] — `data.allowedTags` is a reference to `ALLOWED_TAGS`

`src/purify.ts:1206-1209`:

```ts
_executeHooks(hooks.uponSanitizeElement, currentNode, {
  tagName,
  allowedTags: ALLOWED_TAGS,         // [A] direct reference; hook mutation
                                      //     mutates the very ALLOWED_TAGS the
                                      //     library checks on the next element
});
```

`src/purify.ts:1494-1500` (the matching attribute hook):

```ts
const hookEvent = {
  attrName: '',
  attrValue: '',
  keepAttr: true,
  allowedAttributes: ALLOWED_ATTR,    // [A'] same pattern
  forceKeepAttr: undefined,
};
```

### [B] — `ALLOWED_TAGS = DEFAULT_ALLOWED_TAGS` for default-cfg sanitize calls

`src/purify.ts:527-531`:

```ts
ALLOWED_TAGS =
  objectHasOwnProperty(cfg, 'ALLOWED_TAGS') &&
  arrayIsArray(cfg.ALLOWED_TAGS)
    ? addToSet({}, cfg.ALLOWED_TAGS, transformCaseFunc)
    : DEFAULT_ALLOWED_TAGS;            // [B] reference assignment; ALLOWED_TAGS
                                       //     IS the DEFAULT_ALLOWED_TAGS object
```

(The `ALLOWED_ATTR = DEFAULT_ALLOWED_ATTR` path at `:532-536` is symmetric.)

### The mismatch

A hook author who writes `data.allowedTags['script'] = true` reasonably expects per-call scope — the API name is *"data"*, suggesting per-event payload. But [A] makes this a direct reference, and [B] makes that reference equal to the module-level default for the common default-cfg path. The hook's mutation therefore writes to a *constant* that every subsequent default-cfg sanitize call rebinds to.

The maintainer already recognized this class for the `ADD_TAGS` array path — `src/purify.ts:696-700`:

```ts
} else if (arrayIsArray(cfg.ADD_TAGS)) {
  if (ALLOWED_TAGS === DEFAULT_ALLOWED_TAGS) {
    ALLOWED_TAGS = clone(ALLOWED_TAGS);   // explicitly clone DEFAULT before
                                          // mutating to avoid this pollution
  }
  addToSet(ALLOWED_TAGS, cfg.ADD_TAGS, transformCaseFunc);
}
```

The same defensive clone is missing from the hook code paths.

## Proof of concept

```js
// 1) fresh DOMPurify, default config — script is blocked
DOMPurify.sanitize('<svg><script>alert(1)</script></svg>');
// → "<svg></svg>"

// 2) install a hook that mutates data.allowedTags (natural-looking pattern)
DOMPurify.addHook('uponSanitizeElement', (node, data) => {
  data.allowedTags['script'] = true;
});

// 3) one sanitize call WITH the hook — script survives (expected during the hook)
DOMPurify.sanitize('<svg><script>alert(1)</script></svg>');
// → "<svg><script>alert(1)</script></svg>"

// 4) remove the hook
DOMPurify.removeAllHooks();
DOMPurify.clearConfig();

// 5) sanitize attacker content with default config — POLLUTION PERSISTS
DOMPurify.sanitize('<svg><script>alert(1)</script></svg>');
// → "<svg><script>alert(1)</script></svg>"  ← script survived without any hook

// 6) the only recovery: create a fresh DOMPurify instance
const fresh = DOMPurify(window);
fresh.sanitize('<svg><script>alert(1)</script></svg>');
// → "<svg></svg>"  ← clean
```

Observed (Chromium 148.0.7778.96, DOMPurify HEAD `7996f1d`):

| step | input | output | bypass? |
|---|---|---|---|
| 1 fresh baseline | `<svg><script>__</script></svg>` | `<svg></svg>` | no |
| 1b fresh baseline | `<a onclick=__>x</a>` | `<a>x</a>` | no |
| 2 with hook (script) | `<svg><script>__</script></svg>` | `<svg><script>__</script></svg>` | yes (expected) |
| 2b with hook (onclick) | `<a onclick=__>x</a>` | `<a onclick="__">x</a>` | yes (expected) |
| 3 after `removeAllHooks()` | same | `<svg><script>__</script></svg>` | **YES (pollution)** |
| 3b after `removeAllHooks()` | same | `<a onclick="__">x</a>` | **YES (pollution)** |
| 4 after `clearConfig()` | same | `<svg><script>__</script></svg>` | **YES** |
| 4b after `clearConfig()` | same | `<a onclick="__">x</a>` | **YES** |
| 5 explicit restrictive `cfg.ALLOWED_TAGS=['svg']` | same | `<svg></svg>` | no (cloned set) |
| 6 back to no cfg | same | `<svg><script>__</script></svg>` | **YES** |
| 6b back to no cfg | same | `<a onclick="__">x</a>` | **YES** |
| 7 fresh `DOMPurify(window)` instance | same | `<svg></svg>` | no |
| 7b fresh instance | `<a onclick=__>x</a>` | `<a>x</a>` | no |

## Impact

### Direct

Any application using `DOMPurify` that has any registered hook with the pattern `data.allowedTags[...] = true` or `data.allowedAttributes[...] = true`. The hook need not be designed to be permissive — it might be intended to *temporarily* allow a custom tag for one specific element shape. After the hook has executed even once, every subsequent default-config sanitize call carries the widened defaults, including:

- attacker content rendered via separate code paths (e.g., the same library serving a comments section and a profile bio, where the bio uses the hook and the comments use plain `DOMPurify.sanitize(text)`)
- third-party libraries that call `DOMPurify.sanitize` on the same instance

The bypass survives `DOMPurify.removeAllHooks()` and `DOMPurify.clearConfig()` — the obvious "reset" calls a dev would reach for. Detection requires reading the `DEFAULT_ALLOWED_TAGS` / `DEFAULT_ALLOWED_ATTR` sets directly, which are not part of the public API.

### Indirect / second-order

- **Editor / preview libraries** that compose with DOMPurify — if any consumer registers a hook that mutates `data.allowedTags`, every other consumer's sanitize calls inherit the widening.
- **Test suites** that exercise multiple sanitize configurations — once a test's hook pollutes the defaults, later tests that assume default behavior may pass with widened defaults and miss real regressions.
- **Long-running servers** (SSR, edge functions) that reuse a single DOMPurify instance — pollution accumulates over the process lifetime.

### Why the existing maintainer defense for `ADD_TAGS` doesn't catch this

`src/purify.ts:696-700` already documents awareness:

```ts
} else if (arrayIsArray(cfg.ADD_TAGS)) {
  if (ALLOWED_TAGS === DEFAULT_ALLOWED_TAGS) {
    ALLOWED_TAGS = clone(ALLOWED_TAGS);
  }
  addToSet(ALLOWED_TAGS, cfg.ADD_TAGS, transformCaseFunc);
}
```

The clone-before-mutate pattern is exactly what's needed at the hook callsites (`:1206-1209` and `:1494-1500`) but was not extended there. The new entries this report's bypass adds to the defaults survive the same way `ADD_TAGS` array entries would have survived before that fix landed.

## Suggested fix

Three minimal-impact options, in order of preference:

1. **Hand the hook a defensive copy** (most surgical):

   ```ts
   _executeHooks(hooks.uponSanitizeElement, currentNode, {
     tagName,
     allowedTags: { ...ALLOWED_TAGS },     // shallow copy; mutations stay scoped
   });
   ```

   Doc note: "`data.allowedTags` is a snapshot; to widen the live set, use `cfg.ADD_TAGS` or set the value to true in the snapshot and check the snapshot from a subsequent attribute hook." Hooks that read it for inspection still work; hooks that intended cross-call mutation must be rewritten to use a proper config path (which is the correct API anyway).

2. **Clone-on-write inside the hook path**, mirroring the existing `ADD_TAGS` defense at `:696-700`: detect that `ALLOWED_TAGS === DEFAULT_ALLOWED_TAGS` after the hook returns, and if so, replace it with a clone for subsequent processing. This preserves the live-mutation semantics for in-call effects while preventing cross-call leakage.

3. **Lazy-clone `ALLOWED_TAGS`/`ALLOWED_ATTR` from defaults on first mutation**: install a Proxy or accessor that triggers a clone before mutation. Largest surface area, but bulletproof.

Option (1) is the cleanest API contract: hook event objects should be event-local, never references to library-internal state.

## References
- https://github.com/cure53/DOMPurify/security/advisories/GHSA-76mc-f452-cxcm
- https://github.com/cure53/DOMPurify
