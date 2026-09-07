# [H] Server-Side Request Forgery via /_image endpoint in Astro Cloudflare adapter

## Summary
Severity: High
Advisory: GHSA-qpr4-c339-7vq8
CVE: CVE-2025-58179
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-09-04
Source: https://github.com/advisories/GHSA-qpr4-c339-7vq8
Type: github-advisory

## Affected
- npm: `@astrojs/cloudflare` — affected >=11.0.3 <12.6.6

## Details
### Summary

When using Astro's Cloudflare adapter (`@astrojs/cloudflare`) configured with `output: 'server'` while using the default `imageService: 'compile'`, the generated image optimization endpoint doesn't check the URLs it receives, allowing content from unauthorized third-party domains to be served.

### Details

On-demand rendered sites built with Astro include an `/_image` endpoint, which returns optimized versions of images.

The `/_image` endpoint is restricted to processing local images bundled with the site and also supports remote images from domains the site developer has manually authorized (using the [`image.domains`](https://docs.astro.build/en/reference/configuration-reference/#imagedomains) or [`image.remotePatterns`](https://docs.astro.build/en/reference/configuration-reference/#imageremotepatterns) options).

However, a bug in impacted versions of the `@astrojs/cloudflare` adapter for deployment on Cloudflare’s infrastructure, allows an attacker to bypass the third-party domain restrictions and serve any content from the vulnerable origin.

### PoC

1. Create a new minimal Astro project (`astro@5.13.3`)

2. Configure it to use the Cloudflare adapter (`@astrojs/cloudflare@12.6.5`) and server output:

   ```js
   // astro.config.mjs
   import { defineConfig } from 'astro/config';
   import cloudflare from '@astrojs/cloudflare';

   export default defineConfig({
     output: 'server',
     adapter: cloudflare(),
   });
   ```

3. Deploy to Cloudflare Pages or Workers

4. Append `/_image?href=https://placehold.co/600x400` to the deployment URL.

7. This will serve the placeholder image from the unauthorised `placehold.co` domain.

### Impact

Allows a non-authorized third-party to create URLs on an impacted site’s origin that serve unauthorized content. This includes the risk of server-side request forgery (SSRF) and by extension cross-site scripting (XSS) if a user follows a link to a maliciously crafted URL.

## References
- https://github.com/withastro/astro/security/advisories/GHSA-qpr4-c339-7vq8
- https://nvd.nist.gov/vuln/detail/CVE-2025-58179
- https://github.com/withastro/astro/commit/9ecf3598e2b29dd74614328fde3047ea90e67252
- https://github.com/withastro/astro
