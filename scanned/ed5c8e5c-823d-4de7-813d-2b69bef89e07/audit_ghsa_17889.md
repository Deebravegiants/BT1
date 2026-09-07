# [M] Astro allows unauthorized third-party images in _image endpoint

## Summary
Severity: Medium
Advisory: GHSA-xf8x-j4p2-f749
CVE: CVE-2025-55303
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-08-19
Source: https://github.com/advisories/GHSA-xf8x-j4p2-f749
Type: github-advisory

## Affected
- npm: `astro` — affected >=5.0.0-alpha.0 <5.13.2
- npm: `@astrojs/node` — affected >=0 <9.1.1
- npm: `astro` — affected >=0 <4.16.19

## Details
### Summary

In affected versions of `astro`, the image optimization endpoint in projects deployed with on-demand rendering allows images from unauthorized third-party domains to be served.

### Details

On-demand rendered sites built with Astro include an `/_image` endpoint which returns optimized versions of images.

The `/_image` endpoint is restricted to processing local images bundled with the site and also supports remote images from domains the site developer has manually authorized (using the [`image.domains`](https://docs.astro.build/en/reference/configuration-reference/#imagedomains) or [`image.remotePatterns`](https://docs.astro.build/en/reference/configuration-reference/#imageremotepatterns) options).

However, a bug in impacted versions of `astro` allows an attacker to bypass the third-party domain restrictions by using a protocol-relative URL as the image source, e.g. `/_image?href=//example.com/image.png`.

### Proof of Concept

1. Create a new minimal Astro project (`astro@5.13.0`).

2. Configure it to use the Node adapter (`@astrojs/node@9.1.0` — newer versions are not impacted):

   ```js
   // astro.config.mjs
   import { defineConfig } from 'astro/config';
   import node from '@astrojs/node';

   export default defineConfig({
   	adapter: node({ mode: 'standalone' }),
   });
   ```

3. Build the site by running `astro build`.

4. Run the server, e.g. with `astro preview`.

5. Append `/_image?href=//placehold.co/600x400` to the preview URL, e.g. <http://localhost:4321/_image?href=//placehold.co/600x400>

6. The site will serve the image from the unauthorized `placehold.co` origin.

### Impact

Allows a non-authorized third-party to create URLs on an impacted site’s origin that serve unauthorized image content.
In the case of SVG images, this could include the risk of cross-site scripting (XSS) if a user followed a link to a maliciously crafted SVG.

## References
- https://github.com/withastro/astro/security/advisories/GHSA-xf8x-j4p2-f749
- https://nvd.nist.gov/vuln/detail/CVE-2025-55303
- https://github.com/withastro/astro/commit/4d16de7f95db5d1ec1ce88610d2a95e606e83820
- https://github.com/withastro/astro
