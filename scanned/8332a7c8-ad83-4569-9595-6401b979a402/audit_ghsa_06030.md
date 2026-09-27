# [M] Nuxt: Unauthorized Component Instantiation via Server Island Props

## Summary
Severity: Medium
Advisory: GHSA-48hr-524c-v5w3
CVE: CVE-2026-71318
CWE: CWE-20
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-08-05
Source: https://github.com/advisories/GHSA-48hr-524c-v5w3
Type: github-advisory

## Affected
- npm: `nuxt` — affected >=4.0.0 <4.5.1
- npm: `nuxt` — affected >=3.1.0 <3.21.10

## Details
## Impact

Nuxt server islands accept props via the `/__nuxt_island/` endpoint. When an application has a server island component that forwards props directly into Vue's dynamic component resolution (`<component :is>`, `resolveDynamicComponent`, or `h()`), an attacker can pass a plain string value (rather than a component definition) to instantiate any globally-registered Vue component or any native HTML element.

For example:
```json
{ "as": "SomeGlobalComponent" }
```

...resolves and renders `SomeGlobalComponent` if it is globally registered, even though the attacker should only be able to drive props for the island's declared component. Similarly, `{ "as": "iframe" }` renders an `<iframe>` element.

Unlike the primary RCE vector (GHSA-9473-5f9j-94wq), this does **not** require `vue.runtimeCompiler` to be enabled. A plain string prop is sufficient to trigger component resolution. The `template`/`render` key guard that addresses the RCE vector does not block plain string values.

Some component libraries expose a polymorphic `as` / `asChild` prop that forwards its value into `<component :is>`; `@nuxt/ui` (via `reka-ui`) is a widely used example. An application is affected if such a component receives the attacker-controlled value inside a server island. Note this does not require explicit prop forwarding: island props the island component does not declare fall through as attributes onto its single root element, so an island whose root is a `reka-ui` / `@nuxt/ui` component receives the attacker's `as` value implicitly. Unlike the RCE vector, no `vue.runtimeCompiler` is required, which makes this vector reachable in more configurations. These libraries are not themselves vulnerable; they are noted only because they commonly provide the dynamic-component sink. Installing `@nuxt/ui` does not by itself register any component as a server island: the application must define the island (a `.server.vue` file).

## Mitigating factors

- Exploitation requires a server island component that puts an attacker-controlled value onto a dynamic-component path (`<component :is>`, `resolveDynamicComponent`, `h()`, or a polymorphic `as` / `asChild` prop), either explicitly or via attribute fallthrough when the island's root is such a component.
- Reachable components are limited to what is actually in the island app's global registry. In a default pages-enabled app that is `RouterView` and `RouterLink` (both registered globally by the pages router plugin, which runs even in component islands), plus any `components/global/` component and any component a module registers globally. `RouterLink` in particular renders an attacker-influenced `<a>` (and, because an island that declares no props forwards all props, `to` and other `RouterLink` props ride the same fallthrough). Vue built-ins (`Transition`, `KeepAlive`, `Teleport`, `Suspense`) and Nuxt auto-imports (`ClientOnly`, `NuxtLink`, `NuxtPage`, etc.) are NOT in the island app's global registry and cannot be resolved this way; an unresolved name instead renders as a native HTML element (the element-injection half of this issue).
- Declaring the props an island accepts, or setting `inheritAttrs: false` on it, prevents an undeclared `as` from falling through to a polymorphic root and neutralizes this vector.
- Arbitrary JavaScript execution is not possible through this vector (no `template`/`render` compilation).
- Island component names are constrained to the build-time component registry; an attacker cannot resolve arbitrary components.

## Affected versions

Nuxt `>=3.1.0 <3.21.10` and `>=4.0.0 <4.5.1`, with component islands active. The island prop-forwarding behavior has existed since server islands were introduced in v3.1.0, and this vector does not depend on `vue.runtimeCompiler`. Nuxt 2 is not affected.

Note the patch (below) closes the implicit attribute-fallthrough path, which is the majority case. An island that *explicitly* forwards an untrusted prop into dynamic component resolution (or forwards it under a prop name other than `as`) remains the application's responsibility in every version; see Workarounds.

## Patches

Fixed in `nuxt@4.5.1` and `nuxt@3.21.10`. Patched releases reject a top-level `as` island prop (HTTP 400 at the `/__nuxt_island/` endpoint). This closes the implicit path: island props an island does not declare fall through as attributes onto its single root, so a top-level `as` would otherwise reach a polymorphic root component's `as` prop (the `reka-ui` / `@nuxt/ui` convention) and drive dynamic component resolution without the author binding it. Rejecting the top-level `as` prop blocks that fallthrough while leaving nested data and other prop names untouched.

The framework deliberately does not attempt to block every case: it cannot safely tell a string used as data from one used as a component selector, and it has no island-local hook into Vue's `h()` or `resolveDynamicComponent()`. An island that explicitly forwards an untrusted value into `<component :is>` / `h()` / `resolveDynamicComponent()`, or that forwards it under a different polymorphic prop name, is therefore not covered by the patch and must follow the guidance below. The Nuxt documentation now warns against this.

## Workarounds

Upgrade to `nuxt@4.5.1` or `nuxt@3.21.10`. That upgrade also removes the related object-prop RCE (GHSA-9473-5f9j-94wq). In addition, in any version:

1. Do not forward island props into `<component :is>`, `resolveDynamicComponent`, or `h()`. Map an untrusted discriminator through a closed allowlist of imported component definitions instead of passing the raw prop value.
2. Declare the props an island accepts, or set `inheritAttrs: false` on it, so request input cannot fall through to a polymorphic root component.
3. Avoid registering sensitive components globally that could leak information if instantiated by an attacker.

## References
- https://github.com/nuxt/nuxt/security/advisories/GHSA-48hr-524c-v5w3
- https://github.com/nuxt/nuxt
- https://github.com/nuxt/nuxt/releases/tag/v3.21.10
- https://github.com/nuxt/nuxt/releases/tag/v4.5.1
