# [H] Budibase: Path traversal in plugin file upload enables arbitrary directory deletion and file write

## Summary
Severity: High
Advisory: GHSA-2wfh-rcwf-wh23
CVE: CVE-2026-35214
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:N/I:H/A:H (CVSS_V3)
Published: 2026-04-04
Source: https://github.com/advisories/GHSA-2wfh-rcwf-wh23
Type: github-advisory

## Affected
- npm: `@budibase/server` — affected >=0 <3.33.4

## Details
## Summary

The plugin file upload endpoint (`POST /api/plugin/upload`) passes the user-supplied filename directly to `createTempFolder()` without sanitizing path traversal sequences. An attacker with Global Builder privileges can craft a multipart upload with a filename containing `../` to delete arbitrary directories via `rmSync` and write arbitrary files via tarball extraction to any filesystem path the Node.js process can access.

## Severity

- **Attack Vector:** Network — exploitable via the plugin upload HTTP API
- **Attack Complexity:** Low — no special conditions; a single crafted multipart request suffices
- **Privileges Required:** High — requires Global Builder role (`GLOBAL_BUILDER` permission)
- **User Interaction:** None
- **Scope:** Changed — the plugin upload feature is scoped to a temp directory, but the traversal escapes to the host filesystem
- **Confidentiality Impact:** None — the vulnerability enables deletion and writing, not reading
- **Integrity Impact:** High — attacker can delete arbitrary directories and write arbitrary files via tarball extraction
- **Availability Impact:** High — recursive deletion of application or system directories causes denial of service

### Severity Rationale

 Despite the real filesystem impact, severity is bounded by the requirement for Global Builder privileges (PR:H), which is the highest non-admin role in Budibase. In self-hosted deployments the Global Builder may already have server access, further reducing practical impact. In cloud/multi-tenant deployments the impact is more significant as it could affect the host infrastructure.

## Affected Component

- `packages/server/src/api/controllers/plugin/file.ts` — `fileUpload()` (line 15)
- `packages/server/src/utilities/fileSystem/filesystem.ts` — `createTempFolder()` (lines 78-91)

## Description

### Unsanitized filename flows into filesystem operations

In `packages/server/src/api/controllers/plugin/file.ts`, the uploaded file's name is used directly after stripping the `.tar.gz` suffix:

```typescript
// packages/server/src/api/controllers/plugin/file.ts:8-19
export async function fileUpload(file: KoaFile) {
  if (!file.name || !file.path) {
    throw new Error("File is not valid - cannot upload.")
  }
  if (!file.name.endsWith(".tar.gz")) {
    throw new Error("Plugin must be compressed into a gzipped tarball.")
  }
  const path = createTempFolder(file.name.split(".tar.gz")[0])
  await extractTarball(file.path, path)

  return await getPluginMetadata(path)
}
```

The `file.name` originates from the `Content-Disposition` header's `filename` field in the multipart upload, parsed by formidable (via koa-body 4.2.0). Formidable does not sanitize path traversal sequences from filenames.

The `createTempFolder` function in `packages/server/src/utilities/fileSystem/filesystem.ts` uses `path.join()` which resolves `../` sequences, then performs destructive filesystem operations:

```typescript
// packages/server/src/utilities/fileSystem/filesystem.ts:78-91
export const createTempFolder = (item: string) => {
  const path = join(budibaseTempDir(), item)
  try {
    // remove old tmp directories automatically - don't combine
    if (fs.existsSync(path)) {
      fs.rmSync(path, { recursive: true, force: true })
    }
    fs.mkdirSync(path)
  } catch (err: any) {
    throw new Error(`Path cannot be created: ${err.message}`)
  }

  return path
}
```

The `budibaseTempDir()` returns `/tmp/.budibase` (from `packages/backend-core/src/objectStore/utils.ts:33`). With a filename like `../../etc/target.tar.gz`, `path.join("/tmp/.budibase", "../../etc/target")` resolves to `/etc/target`.

### Inconsistent defenses confirm the gap

The codebase is aware of the risk in similar paths:

1. **Safe path in `utils.ts`**: The `downloadUnzipTarball` function (for NPM/GitHub/URL plugin sources) generates a random name server-side:
   ```typescript
   // packages/server/src/api/controllers/plugin/index.ts:68
   const name = "PLUGIN_" + Math.floor(100000 + Math.random() * 900000)
   ```
   This is safe because `name` never contains user input.

2. **Safe path in `objectStore.ts`**: Other uses of `budibaseTempDir()` use UUID-generated names:
   ```typescript
   // packages/backend-core/src/objectStore/objectStore.ts:546
   const outputPath = join(budibaseTempDir(), v4())
   ```

3. **Sanitization exists but is not applied**: The codebase has `sanitizeKey()` in `objectStore.ts` for sanitizing object store paths, but no equivalent is applied to `createTempFolder`'s input.

The file upload path is the only caller of `createTempFolder` that passes unsanitized user input.

### Execution chain

1. Authenticated Global Builder sends `POST /api/plugin/upload` with a multipart file whose `Content-Disposition` filename contains path traversal (e.g., `../../etc/target.tar.gz`)
2. koa-body/formidable parses the upload, setting `file.name` to the raw filename from the header
3. `controller.upload` → `sdk.plugins.processUploaded()` → `fileUpload(file)`
4. `.endsWith(".tar.gz")` check passes (the suffix is present)
5. `.split(".tar.gz")[0]` extracts `../../etc/target`
6. `createTempFolder("../../etc/target")` is called
7. `path.join("/tmp/.budibase", "../../etc/target")` resolves to `/etc/target`
8. `fs.rmSync("/etc/target", { recursive: true, force: true })` — **deletes the target directory recursively**
9. `fs.mkdirSync("/etc/target")` — **creates a directory at the traversed path**
10. `extractTarball(file.path, "/etc/target")` — **extracts attacker-controlled tarball contents to the traversed path**

## Proof of Concept

```bash
# Create a minimal tarball with a test file
mkdir -p /tmp/plugin-poc && echo "pwned" > /tmp/plugin-poc/test.txt
tar czf /tmp/poc-plugin.tar.gz -C /tmp/plugin-poc .

# Upload with a traversal filename targeting /tmp/pwned (non-destructive demo)
curl -X POST 'http://localhost:10000/api/plugin/upload' \
  -H 'Cookie: <global_builder_session_cookie>' \
  -F "file=@/tmp/poc-plugin.tar.gz;filename=../../tmp/pwned.tar.gz"

# Result: server executes:
#   rm -rf /tmp/pwned        (if exists)
#   mkdir /tmp/pwned
#   tar xzf <upload> -C /tmp/pwned
# Verify: ls /tmp/pwned/test.txt
```

## Impact

- **Arbitrary directory deletion**: `rmSync` with `{ recursive: true, force: true }` deletes any directory the Node.js process can access, including application data directories
- **Arbitrary file write**: Tarball extraction writes attacker-controlled files to any writable path, potentially overwriting application code, configuration, or system files
- **Denial of service**: Deleting critical directories (e.g., the application's data directory, node_modules, or system directories) crashes the application
- **Potential code execution**: In containerized deployments (common for Budibase) where Node.js runs as root, an attacker could overwrite startup scripts or application code to achieve remote code execution on subsequent restarts

## Recommended Remediation

### Option 1: Sanitize at `createTempFolder` (preferred — protects all callers)

```typescript
import { join, resolve } from "path"

export const createTempFolder = (item: string) => {
  const tempDir = budibaseTempDir()
  const resolved = resolve(tempDir, item)

  // Ensure the resolved path is within the temp directory
  if (!resolved.startsWith(tempDir + "/") && resolved !== tempDir) {
    throw new Error("Invalid path: directory traversal detected")
  }

  try {
    if (fs.existsSync(resolved)) {
      fs.rmSync(resolved, { recursive: true, force: true })
    }
    fs.mkdirSync(resolved)
  } catch (err: any) {
    throw new Error(`Path cannot be created: ${err.message}`)
  }

  return resolved
}
```

### Option 2: Sanitize at the upload handler (defense-in-depth)

Strip path components from the filename before use:

```typescript
import path from "path"

export async function fileUpload(file: KoaFile) {
  if (!file.name || !file.path) {
    throw new Error("File is not valid - cannot upload.")
  }
  if (!file.name.endsWith(".tar.gz")) {
    throw new Error("Plugin must be compressed into a gzipped tarball.")
  }
  // Strip directory components from the filename
  const safeName = path.basename(file.name).split(".tar.gz")[0]
  const dir = createTempFolder(safeName)
  await extractTarball(file.path, dir)

  return await getPluginMetadata(dir)
}
```

Both options should ideally be applied together for defense-in-depth.

## Credit

This vulnerability was discovered and reported by [bugbunny.ai](https://bugbunny.ai).

## References
- https://github.com/Budibase/budibase/security/advisories/GHSA-2wfh-rcwf-wh23
- https://nvd.nist.gov/vuln/detail/CVE-2026-35214
- https://github.com/Budibase/budibase/pull/18240
- https://github.com/Budibase/budibase/commit/6344d06d703660fd05995e61d581593c2349c879
- https://github.com/Budibase/budibase
- https://github.com/Budibase/budibase/releases/tag/3.33.4
