# [M] Nuxt OG Image vulnerable to Server-Side Request Forgery via user-controlled parameters

## Summary
Severity: Medium
Advisory: GHSA-pqhr-mp3f-hrpp
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-pqhr-mp3f-hrpp
Type: github-advisory

## Affected
- npm: `nuxt-og-image` — affected >=0 <6.2.5

## Details
**Product:** Nuxt OG Image
**Version:** < 6.2.5
**CWE-ID:** [CWE-918](https://cwe.mitre.org/data/definitions/918.html): Server-Side Request Forgery

## Description

The image generation endpoint (`/_og/d/`) accepts user-controlled parameters that are passed to the server-side renderer without proper validation or filtering. An attacker can trigger server-side requests to internal network addresses through multiple vectors.

## Impact

- Scanning internal ports and services inaccessible from the outside
- Reading sensitive data from cloud infrastructure metadata services (tokens, credentials) when verbose error output is enabled

## Attack Vectors

Three distinct vectors were identified, all exploiting the same underlying lack of URL validation:

### Vector 1: CSS `background-image` injection via `style` parameter

```
GET /_og/d/og.png?style=background-image:+url('http://127.0.0.1:8888/secret')
```

### Vector 2: `<img src>` injection via `html` parameter

```
GET /_og/d/og.png?html=<img src="http://127.0.0.1:8888/secret">
```

When verbose errors are enabled, the response content is leaked in base64-encoded error messages.

### Vector 3: SVG `<image href>` injection via `html` parameter

```
GET /_og/d/og.png?html=<svg><image href="http://127.0.0.1:8888/secret"></svg>
```

## Mitigation

Fixed in v6.2.5. The image source plugin now blocks requests to private IP ranges (IPv4/IPv6), loopback addresses, link-local addresses, and cloud metadata endpoints. Decimal/hexadecimal IP encoding bypasses are also handled.

## Credits

Researcher: Dmitry Prokhorov (Positive Technologies)

## References
- https://github.com/nuxt-modules/og-image/security/advisories/GHSA-pqhr-mp3f-hrpp
- https://github.com/nuxt-modules/og-image
