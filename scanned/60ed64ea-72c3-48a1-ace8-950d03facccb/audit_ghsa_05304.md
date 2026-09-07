# [H] Angular Client Hydration DOM Clobbering & Response-Cache Poisoning

## Summary
Severity: High
Advisory: GHSA-rgjc-h3x7-9mwg
CVE: CVE-2026-54267
CWE: CWE-471, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-15
Source: https://github.com/advisories/GHSA-rgjc-h3x7-9mwg
Type: github-advisory

## Affected
- npm: `@angular/core` — affected >=22.0.0-next.0 <22.0.1
- npm: `@angular/core` — affected >=21.0.0-next.0 <21.2.17
- npm: `@angular/core` — affected >=20.0.0-next.0 <20.3.25
- npm: `@angular/core` — affected >=0

## Details
To optimize client-side bootstrap in Server-Side Rendered (SSR) environments, Angular supports **Hydration** via `provideClientHydration()`. During SSR, Angular serializes the application's runtime state (such as cached `HttpClient` responses) and outputs it into the HTML stream as a `<script>` tag with a predictable identifier:

```html
<script type="application/json" id="ng-state">
    {"some-api-url": {"body": ...}}
</script>
````

During client bootstrap, Angular recovers this state by looking up the element via `document.getElementById('ng-state')` and parsing its text content.

Because the DOM element lookup for the state container is predictable and relies solely on the ID selector (`ng-state`), it is susceptible to **DOM Clobbering**.

If the application binds untrusted user input or CMS content to element properties such as `id` (e.g., `<div [id]="userInput">` or `<a id="ng-state">`) *before* the genuine `<script>` tag is parsed by the browser, the attacker-controlled element takes precedence in the DOM lookup.

During hydration, when Angular calls `document.getElementById('ng-state')`, the browser returns the attacker's clobbered element. Angular then attempts to parse the text content or attributes of this clobbered element as JSON.

### Impact

By clobbering the state element, the attacker can inject a custom JSON payload into Angular's `TransferState` cache. The most critical exploitation vector is poisoning the **HTTP Transfer Cache**.

1. The attacker injects a clobbered `ng-state` element containing custom JSON.  
2. The JSON maps a key (representing a target API endpoint URL) to a malicious payload of the attacker's choice.  
3. During client-side initialization, Angular's `HttpClient` checks `TransferState` before making requests. Finding the poisoned key, `HttpClient` returns the forged response instantly instead of requesting the genuine backend API.

Depending on how the application processes and renders the affected API response, this can lead to:

* **DOM-based Cross-Site Scripting (XSS)** if poisoned fields are rendered using unsafe bindings.  
* **Privilege Escalation** by spoofing user info or session details retrieved from poisoned API payloads.  
* **UI Hijacking** and redirection by spoofing configuration endpoints.

### Patched Versions

* 22.0.1  
* 21.2.17  
* 20.3.25

### Workarounds

If you cannot immediately update to a patched Angular version, apply the following workarounds:

#### A. Avoid Dynamic/User-Controlled IDs

Avoid binding raw user-supplied values or dynamic CMS IDs directly to element attributes. If dynamic IDs are required, sanitize them or prepend a static safe prefix:

```html
<!-- Vulnerable Pattern -->
<div [id]="userControlledInput">...</div>

<!-- Mitigated Pattern -->
<div [id]="'safe-prefix-' + userControlledInput">...</div>
```

#### B. Configure a Custom Application ID

Declaring a unique, non-predictable `APP_ID` changes the ID suffix of the state element, making it harder for attackers to predict and target:

```ts
// app.config.ts

import { APP_ID } from '@angular/core';
import { provideClientHydration } from '@angular/platform-browser';

export const appConfig = {
  providers: [
    { provide: APP_ID, useValue: 'unique-obfuscated-app-id' },
    provideClientHydration()
  ]
};

```

This changes the state element lookup ID from `ng-state` to `unique-obfuscated-app-id-state`.

## References
- https://github.com/angular/angular/security/advisories/GHSA-rgjc-h3x7-9mwg
- https://nvd.nist.gov/vuln/detail/CVE-2026-54267
- https://github.com/angular/angular/pull/69064
- https://github.com/angular/angular/commit/6bde84fa8e6a5770b54040fbbc9bf10d5d0386fa
- https://github.com/angular/angular
