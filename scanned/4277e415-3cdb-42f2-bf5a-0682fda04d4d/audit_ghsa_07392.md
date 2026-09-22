# [M] @nuxt/ui: UAuthForm / UForm SSR markup omits `method`, leaking credentials via GET if submitted before hydration

## Summary
Severity: Medium
Advisory: GHSA-gj2h-2fpw-fhv9
CWE: CWE-200, CWE-598
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-gj2h-2fpw-fhv9
Type: github-advisory

## Affected
- npm: `@nuxt/ui` — affected >=0 <4.8.1

## Details
### Summary

`UForm` and `UAuthForm` render a server-side `<form>` element with no `method` and no `action` attribute, relying on a hydrated `@submit.prevent` handler to intercept submission. If a user submits the form before Vue hydration has attached the handler (autofill plus Enter on a slow network, JS bundle blocked by CSP or CDN failure, etc.), the browser performs the native default: a `GET` to the current URL with every named field, including `<input type="password">`, serialised into the query string.

### Details

`src/runtime/components/Form.vue` (around the template's `<form>` element) emits:

```vue
<component
  :is="parentBus ? 'div' : 'form'"
  :id="formId"
  ref="formRef"
  :class="ui({ class: [uiProp?.base, props.class] })"
  @submit.prevent="onSubmitWrapper"
>
```

No `method`, no `action`. `@submit.prevent` is the only thing stopping native submission, and it only exists after hydration. `UAuthForm` composes `UForm` and inherits the same shape.

The SSR snapshot of `UAuthForm` (`test/components/__snapshots__/AuthForm.spec.ts.snap`) shows the rendered markup, with `<input type="password" name="password">` inside a `<form>` that has no `method`.

### Proof of concept

Reported by @nimonian:

1. Create a minimal Nuxt app with a `UAuthForm`.
2. Build for production and visit in a browser with network throttling at 4G or slower.
3. Enter credentials.
4. Submit (or let autofill + Enter fire before hydration).

The URL becomes `/login?email=…&password=…`. Reproducible deterministically in Playwright by triggering submit immediately on `load`.

### Impact

Any application using `UAuthForm` (or `UForm` with credential-shaped fields) as documented. The cleartext password lands in:

- the address bar,
- `window.history`,
- the `Referer` header of every same-origin subresource fetched from the resulting URL,
- access logs of any reverse proxy, CDN, or WAF that records request URLs.

### Patch

Default the rendered `<form>` to `method="post"` so the pre-hydration fallback submits as POST rather than GET. Vue's `@submit.prevent` still intercepts the hydrated case; the attribute only matters in the race window. Applications that explicitly want native GET submission can opt back in by passing `method="get"`.

### Credit

Reported by @nimonian. Originally filed as `GHSA-92g7-2fpq-hmq8` against `nuxt/nuxt`; moved here because the affected code lives in `@nuxt/ui`.

## References
- https://github.com/nuxt/ui/security/advisories/GHSA-gj2h-2fpw-fhv9
- https://github.com/nuxt/ui/pull/6512
- https://github.com/nuxt/ui
- https://github.com/nuxt/ui/releases/tag/v4.8.1
