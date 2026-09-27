# [M] @astrojs/netlify broadens Astro image.remotePatterns in Netlify Image CDN config

## Summary
Severity: Medium
Advisory: GHSA-529g-xq4f-cw38
CVE: CVE-2026-54300
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-529g-xq4f-cw38
Type: github-advisory

## Affected
- npm: `@astrojs/netlify` — affected >=0 <7.0.13

## Details
## Summary

`@astrojs/netlify` converts Astro `image.remotePatterns` into Netlify Image CDN `images.remote_images` regular expressions with broader semantics than Astro's canonical matcher. A single wildcard hostname such as `*.example.com` is converted to an optional subdomain regex, so the apex host matches. A single wildcard pathname such as `/ok/*` is converted without end anchoring, so deeper paths match by prefix.

## Technical details

The Netlify adapter generates regex strings for Netlify Image CDN from `image.remotePatterns`. For `*.example.com`, it emits `([a-z0-9-]+\\.)?example\\.com`, which makes the subdomain optional. Astro's canonical helper requires exactly one subdomain and rejects the apex host.

For `/ok/*`, the adapter emits a segment regex but does not anchor the end of the URL. Netlify's Image CDN implementation treats `images.remote_images` entries as JavaScript regular expressions and calls `.test(sourceImageUrl.href)`, so a URL such as `/ok/a/b.svg` matches the `/ok/a` prefix even though Astro's helper rejects it.

The latest npm package `@astrojs/netlify@7.0.10` contains this conversion logic, and a minimal Astro build writes the broadened patterns into `.netlify/v1/config.json`.

## Reproduction

1. Create an Astro app using `astro@6.3.8` and `@astrojs/netlify@7.0.10`.
2. Configure Netlify output and a restrictive image pattern, for example `remotePatterns: [{ protocol: 'http', hostname: '*.localhost', pathname: '/ok/*' }]`.
3. Build the app and observe that `.netlify/v1/config.json` contains `http://([a-z0-9-]+\\.)?localhost(:[0-9]+)?(\\/ok/[^/?#]+)/?([?][^#]*)?`.
4. Serve a canary SVG on `127.0.0.1:9001`.
5. Request `/.netlify/images?url=http%3A%2F%2Flocalhost%3A9001%2Fok%2Fa.svg&w=100`. Astro's helper rejects the apex `localhost` for `*.localhost`, but Netlify Image CDN accepts it and fetches the canary.
6. As a negative control, request `/.netlify/images?url=http%3A%2F%2Flocalhost%3A9001%2Fnope%2Fa.svg&w=100`. This returns `403 Forbidden: Remote image URL not allowed` and does not hit the canary.
7. Request `/.netlify/images?url=http%3A%2F%2Flocalhost%3A9001%2Fok%2Fa%2Fb.svg&w=100`. Astro's `/ok/*` helper rejects this deeper path, but Netlify Image CDN accepts it and fetches the canary.

## Impact

Any Astro app deployed with `@astrojs/netlify` and a restrictive `image.remotePatterns` config can expose a wider image-fetch boundary than intended. Public requests to the Netlify Image CDN endpoint can fetch URLs that Astro's own matcher would reject, including apex hosts for `*.host` patterns and deeper paths for `/path/*` patterns. The practical impact depends on what the application intended to isolate behind the remote image allowlist, but it can disclose image-like resources from unintended hosts or paths behind the same configured remote origin family.

## Remediation

Generate regexes that exactly match Astro's canonical `matchHostname` and `matchPathname` semantics, and anchor the full URL match before writing `images.remote_images`. In particular, `*.example.com` should require exactly one subdomain and should not match `example.com`, and `/ok/*` should match exactly one additional path segment and should not match `/ok/a/b`.

## References
- https://github.com/withastro/astro/security/advisories/GHSA-529g-xq4f-cw38
- https://nvd.nist.gov/vuln/detail/CVE-2026-54300
- https://github.com/withastro/astro
