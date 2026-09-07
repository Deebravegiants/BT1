# [M] Excalidraw vulnerable to XSS via Mermaid sequence diagram labels (KaTeX rendering)

## Summary
Severity: Medium
Advisory: GHSA-39h7-pwv7-rc3x
CWE: CWE-1395, CWE-79
Ecosystem: npm
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-39h7-pwv7-rc3x
Type: github-advisory

## Affected
- npm: `@excalidraw/excalidraw` — affected >=0.18.0 <0.18.1
- npm: `@excalidraw/mermaid-to-excalidraw` — affected >=0.3.0 <1.1.3

## Details
### Impact

`@excalidraw/excalidraw@0.18.0` depends on a Mermaid conversion package version that resolves to a Mermaid release affected by CVE-2025-54881 / GHSA-7rqq-prvp-x9jh. User-supplied Mermaid sequence diagram labels could trigger XSS through Mermaid’s KaTeX label rendering path.

This is patched in `@excalidraw/excalidraw@0.18.1` by updating `@excalidraw/mermaid-to-excalidraw` to `2.2.2`, which uses a patched Mermaid 11 release.

Moderate severity as this XSS requires manual user action - pasting unsafe Mermaid diagram into the Excalidraw editor. No semi-automated attack vector exists by default (such as accessing a link).

### Patches

- Stable `@excalidraw/excalidraw@0.18.1` is patched.
- Unstable `@excalidraw/excalidraw@next` has resolved to patched builds since `@excalidraw/excalidraw@0.18.0-f29edf` on 2025-08-21.
- Direct consumers of `@excalidraw/mermaid-to-excalidraw` should use `1.1.3` or later.

### Workarounds

None.

### Resources

- Upstream Mermaid advisory: https://github.com/mermaid-js/mermaid/security/advisories/GHSA-7rqq-prvp-x9jh
- CVE-2025-54881

## References
- https://github.com/excalidraw/excalidraw/security/advisories/GHSA-39h7-pwv7-rc3x
- https://github.com/mermaid-js/mermaid/security/advisories/GHSA-7rqq-prvp-x9jh
- https://github.com/excalidraw/excalidraw
- https://github.com/excalidraw/excalidraw/releases/tag/v0.18.1
