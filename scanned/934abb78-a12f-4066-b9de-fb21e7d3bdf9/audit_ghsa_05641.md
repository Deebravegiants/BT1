# [H] svelte is vulnerable to XSS with textarea bind:value

## Summary
Severity: High
Advisory: GHSA-gw32-9rmw-qwww
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:L/VA:N/SC:H/SI:H/SA:N (CVSS_V4)
Published: 2026-01-16
Source: https://github.com/advisories/GHSA-gw32-9rmw-qwww
Type: github-advisory

## Affected
- npm: `svelte` — affected >=3.0.0 <3.59.2

## Details
### Summary

A server-side rendered `<textarea>` with two-way bound value does not have its value correctly escaped in the rendered HTML.

### Details

In SSR, `<textarea bind:value={...}>` does not have its value escaped when it is rendered into the HTML as `<textarea>...</textarea>`.

### PoC

Put this in a server-side-rendered Svelte component:

```
<script>
  let value = `test'"></textarea><script` + `>alert('BIM');</sc` + `ript>`;
</script>

<textarea bind:value />
```

### Impact

- Only affects SSR
- Needs a `<textarea bind:value>` filled by user content via two-way binding

## References
- https://github.com/sveltejs/svelte/security/advisories/GHSA-gw32-9rmw-qwww
- https://github.com/sveltejs/svelte/commit/a31dec5eb30978cff7ff4d77f4bf316841f711bc
- https://github.com/sveltejs/svelte
