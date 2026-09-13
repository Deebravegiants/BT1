# [H] better-helperjs Vulnerable to Directory Traversal via String Prefix Bypass in Static Server

## Summary
Severity: High
Advisory: GHSA-3p34-w4f6-5xh2
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-3p34-w4f6-5xh2
Type: github-advisory

## Affected
- npm: `better-helperjs` — affected >=0 <3.0.6

## Details
## Summary
A directory traversal vulnerability exists in the production static file server of `better-helperjs` (`<= 3.0.5`). Attackers can read arbitrary files located in adjacent directory structures that share the same string prefix as the intended static root directory.

## Details
The framework utilizes a custom static file server engine used when running in `NODE_ENV=production` (`src/ssr/site-server.ts`). Inside the `safeStaticPath()` method, the requested path is checked against the static root directory to prevent directory traversal out of the designated public folder.

However, the validation uses `String.prototype.startsWith()`:
```typescript
  const root = path.resolve(rootDir);
  const resolved = path.resolve(root, `.${decodedPath}`);
  
  if (!resolved.startsWith(root)) {
    return null;
  }
```
This is logically flawed because `startsWith` evaluates plain strings rather than structural directory paths. If the application's assigned `rootDir` is `/app/dist/client`, and an attacker tries to access `/app/dist/client-secrets/database.sqlite`, the string `"/app/dist/client-secrets/database.sqlite"` successfully **starts with** `"/app/dist/client"`. 

Because of this bypass, an attacker can read sensitive files stored inside any adjacent directory traversing through the parent, as long as the adjacent directory name begins with the exact same prefix as the target public directory.

## Impact
- **Severity:** High (7.5)
- **Vector:** `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N`
- **Affected Versions:** `<= 3.0.5`
- **Patched Version:** `>= 3.0.6`

## Proof of Concept
To reproduce this locally on a vulnerable installation:
1. Assume the framework static configuration serves from a `.dist/client` directory.
2. Build the project and create an adjacent prefix secret simulating sensitive deployment structure:
   ```bash
   npm run build
   mkdir -p dist/client-secrets
   echo "EXPOSED_SECRET" > dist/client-secrets/secret.txt
   ```
3. Start the application in Production mode (`NODE_ENV=production tsx server.ts`).
4. Using an HTTP client that doesn't pre-normalize `/../` paths (e.g., `netcat` or raw sockets), send a GET request spanning into the prefix-sharing adjacent folder:
   ```http
   GET /%2e%2e%2fclient-secrets/secret.txt HTTP/1.1
   Host: localhost:4174
   Connection: close
   ```
5. The server incorrectly validates the path and responds with `HTTP/1.1 200 OK` exposing `EXPOSED_SECRET`.

*(Note: Developer environment `npm run dev` servers are immune as static requests are handled defensively by Vite's Dev Middlewares. This vulnerability only triggers upon `production` starts).*

## Remediation / Patches
The path validation block has been updated to mandate exact path separation bounds by enforcing `path.sep` onto the evaluated traversal string.
```typescript
  // Enforces separator OR exact root matches preventing prefix extension
  if (!resolved.startsWith(root + path.sep) && resolved !== root) {
    return null;
  }
```

## Workarounds
If upgrading is temporarily impossible, users can safeguard their environment by ensuring no sensitive directories are deployed adjacent to their static build `client` directories sharing the identical word-prefix string.

## References
- https://github.com/Rigby-Foundation/BetterHelperjs/security/advisories/GHSA-3p34-w4f6-5xh2
- https://github.com/Rigby-Foundation/BetterHelperjs
