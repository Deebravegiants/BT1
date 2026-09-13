# [H] Nuxt: Unauthenticated out-of-memory crash via unbounded v-for expansion in island rendering

## Summary
Severity: High
Advisory: GHSA-hxcr-hm88-mpq6
CVE: CVE-2026-71314
CWE: CWE-1284, CWE-400, CWE-770, CWE-789
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-08-05
Source: https://github.com/advisories/GHSA-hxcr-hm88-mpq6
Type: github-advisory

## Affected
- npm: `nuxt` — affected >=4.0.0 <4.5.1
- npm: `nuxt` — affected >=3.1.0 <3.21.10

## Details
### Impact

An unauthenticated attacker can crash a Nuxt server that renders any island / server component containing a `v-for` over a prop (for example `v-for="n in count"` or a `<slot v-for>`). Because the island URL hash is a non-secret digest of the request, the attacker can compute a valid hash for arbitrary props and send the iterated prop as a large integer. The server then expands the `v-for` to that many nodes during SSR, allocating memory proportional to the attacker's number. Reporter figures: `count=8000000` produced a 142.9 MB response; `count=40000000` (and `items=4000000` on a slot list) produced an out-of-memory crash of the worker from a single ~130-byte request. Both the plain `v-for` path (Vue's `ssrRenderList`) and the slot path (`vforToArray`) are affected.

### Patches

Fixed in `nuxt@4.5.1` and `nuxt@3.21.10`. Island/server-component `v-for` sources are now clamped to a maximum iteration count (`MAX_VFOR_LENGTH = 100000`) at the render boundary, covering the plain path, the `<slot v-for>` element, and the `vforToArray` slot-props helper. Combined with the body-size cap (GHSA-9pgf-384g-p7mv), a single island render can no longer allocate without bound regardless of which `v-for` path is used or whether the prop arrives as an integer or an array.

### Workarounds

Avoid `v-for` directly over an unclamped prop in server components, or clamp the count in the component (`v-for="n in Math.min(count, 1000)"`). A body-size limit in front of `/__nuxt_island/` only mitigates array-shaped inputs, not the integer-amplification case.

### References

- Bound helper: `packages/nuxt/src/app/components/vfor.ts`
- Transform: `packages/nuxt/src/components/plugins/islands-transform.ts`
- Slot helper: `packages/nuxt/src/app/components/utils.ts` (`vforToArray`)

## References
- https://github.com/nuxt/nuxt/security/advisories/GHSA-hxcr-hm88-mpq6
- https://github.com/nuxt/nuxt/commit/4e35ae9babd94be53246e31200232d48438bb34e
- https://github.com/nuxt/nuxt/commit/668cdfdfda41849ed11c1ee5e2067a11fc103b22
- https://github.com/nuxt/nuxt
- https://github.com/nuxt/nuxt/releases/tag/v3.21.10
- https://github.com/nuxt/nuxt/releases/tag/v4.5.1
