# [M] DOMPurify: Prototype Pollution to XSS Bypass via CUSTOM_ELEMENT_HANDLING Fallback

## Summary
Severity: Medium
Advisory: GHSA-v9jr-rg53-9pgp
CVE: CVE-2026-41238
CWE: CWE-1321, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-v9jr-rg53-9pgp
Type: github-advisory

## Affected
- npm: `dompurify` — affected >=3.0.1 <3.4.0

## Details
## Summary

DOMPurify versions 3.0.1 through 3.3.3 (latest) are vulnerable to a prototype pollution-based XSS bypass. When an application uses `DOMPurify.sanitize()` with the default configuration (no `CUSTOM_ELEMENT_HANDLING` option), a prior prototype pollution gadget can inject permissive `tagNameCheck` and `attributeNameCheck` regex values into `Object.prototype`, causing DOMPurify to allow arbitrary custom elements with arbitrary attributes — including event handlers — through sanitization.

## Affected Versions

- **3.0.1 through 3.3.3** (current latest) — all affected
- **3.0.0 and all 2.x versions** — NOT affected (used `Object.create(null)` for initialization, no `|| {}` reassignment)
- The vulnerable `|| {}` reassignment was introduced in the 3.0.0→3.0.1 refactor
- This is **distinct** from GHSA-cj63-jhhr-wcxv (USE_PROFILES Array.prototype pollution, fixed in 3.3.2)
- This is **distinct** from CVE-2024-45801 / GHSA-mmhx-hmjr-r674 (__depth prototype pollution, fixed in 3.1.3)

## Root Cause

In `purify.js` at line 590, during config parsing:

```javascript
CUSTOM_ELEMENT_HANDLING = cfg.CUSTOM_ELEMENT_HANDLING || {};
```

When no `CUSTOM_ELEMENT_HANDLING` is specified in the config (the default usage pattern), `cfg.CUSTOM_ELEMENT_HANDLING` is `undefined`, and the fallback `{}` is used. This plain object inherits from `Object.prototype`.

Lines 591-598 then check `cfg.CUSTOM_ELEMENT_HANDLING` (the original config property) — which is `undefined` — so the conditional blocks that would set `tagNameCheck` and `attributeNameCheck` from the config are never entered.

As a result, `CUSTOM_ELEMENT_HANDLING.tagNameCheck` and `CUSTOM_ELEMENT_HANDLING.attributeNameCheck` resolve via the prototype chain. If an attacker has polluted `Object.prototype.tagNameCheck` and `Object.prototype.attributeNameCheck` with permissive values (e.g., `/.*/`), these polluted values flow into DOMPurify's custom element validation at lines 973-977 and attribute validation, causing all custom elements and all attributes to be allowed.

## Impact

- **Attack type:** XSS bypass via prototype pollution chain
- **Prerequisites:** Attacker must have a prototype pollution primitive in the same execution context (e.g., vulnerable version of lodash, jQuery.extend, query-string parser, deep merge utility, or any other PP gadget)
- **Config required:** Default. No special DOMPurify configuration needed. The standard `DOMPurify.sanitize(userInput)` call is affected.
- **Payload:** Any HTML custom element (name containing a hyphen) with event handler attributes survives sanitization

## Proof of Concept

```javascript
// Step 1: Attacker exploits a prototype pollution gadget elsewhere in the application
Object.prototype.tagNameCheck = /.*/;
Object.prototype.attributeNameCheck = /.*/;

// Step 2: Application sanitizes user input with DEFAULT config
const clean = DOMPurify.sanitize('<x-x onfocus=alert(document.cookie) tabindex=0 autofocus>');

// Step 3: "Sanitized" output still contains the event handler
console.log(clean);
// Output: <x-x onfocus="alert(document.cookie)" tabindex="0" autofocus="">

// Step 4: When injected into DOM, XSS executes
document.body.innerHTML = clean; // alert() fires
```

### Tested configurations that are vulnerable:

| Call Pattern | Vulnerable? |
|---|---|
| `DOMPurify.sanitize(input)` | YES |
| `DOMPurify.sanitize(input, {})` | YES |
| `DOMPurify.sanitize(input, { CUSTOM_ELEMENT_HANDLING: null })` | YES |
| `DOMPurify.sanitize(input, { CUSTOM_ELEMENT_HANDLING: {} })` | NO (explicit object triggers L591 path) |

## Suggested Fix

Change line 590 from:
```javascript
CUSTOM_ELEMENT_HANDLING = cfg.CUSTOM_ELEMENT_HANDLING || {};
```

To:
```javascript
CUSTOM_ELEMENT_HANDLING = cfg.CUSTOM_ELEMENT_HANDLING || create(null);
```

The `create(null)` function (already used elsewhere in DOMPurify, e.g., in `clone()`) creates an object with no prototype, preventing prototype chain inheritance.

### Alternative application-level mitigation:

Applications can protect themselves by always providing an explicit `CUSTOM_ELEMENT_HANDLING` in their config:

```javascript
DOMPurify.sanitize(input, {
  CUSTOM_ELEMENT_HANDLING: {
    tagNameCheck: null,
    attributeNameCheck: null
  }
});
```

## Timeline

- **2026-04-04:** Vulnerability discovered during automated DOMPurify fuzzing research (Fermat project)
- **2026-04-04:** Confirmed in Chrome browser with DOMPurify 3.3.3
- **2026-04-04:** Verified distinct from GHSA-cj63-jhhr-wcxv and CVE-2024-45801
- **2026-04-04:** Advisory drafted, responsible disclosure initiated

## Credit

https://github.com/trace37labs

## References
- https://github.com/cure53/DOMPurify/security/advisories/GHSA-v9jr-rg53-9pgp
- https://nvd.nist.gov/vuln/detail/CVE-2026-41238
- https://github.com/cure53/DOMPurify
- https://github.com/cure53/DOMPurify/releases/tag/3.4.0
