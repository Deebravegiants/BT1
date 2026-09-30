# [H] MCPHub has Path Traversal via Malicious MCPB Manifest Name

## Summary
Severity: High
Advisory: GHSA-p3h2-2j4p-p83g
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-22
Source: https://github.com/advisories/GHSA-p3h2-2j4p-p83g
Type: github-advisory

## Affected
- npm: `@samanhappy/mcphub` — affected >=0 <0.12.13

## Details
**MCPB File Upload Handler** extracts a ZIP file and reads `manifest.json` from it. The `name` field in the manifest is directly concatenated into a file path (line 107) without any sanitization or path traversal character validation. An attacker can craft a malicious MCPB file where `manifest.name` is set to something like `../../../etc/malicious`, causing the file to be extracted to an arbitrary location on the file system. The `cleanupOldMcpbServer` function (line 110) also uses the unsanitized name, potentially allowing deletion of arbitrary directories.

## 1. Summary
- **Vulnerability Type**: Path Traversal (CWE-22)
- **Sink Location**: src/controllers/mcpbController.ts:107
- **Vulnerability Description**: The `name` field from an uploaded MCPB manifest is used directly, without sanitization or normalization, to construct a file system path for directory creation and move operations, which may lead to path traversal attacks.

## 2. Analysis Logic

### Step 1: Inspect the identified sink (src/controllers/mcpbController.ts:106-116)
I examined the upload handler and located the file system sink where `manifest.name` is used to build the final extraction path and write files to that path.

```ts
// src/controllers/mcpbController.ts:106-116
// Use server name as the final extract directory for automatic version management
const finalExtractDir = path.join(path.dirname(mcpbFilePath), `server-${manifest.name}`);

// Clean up any existing version of this server
cleanupOldMcpbServer(manifest.name);
if (!fs.existsSync(finalExtractDir)) {
  fs.mkdirSync(finalExtractDir, { recursive: true });
}

// Move the temporary directory to the final location
fs.renameSync(tempExtractDir, finalExtractDir);
```

Analysis: `manifest.name` is used to build `finalExtractDir`, which is then operated on by `fs.mkdirSync` and `fs.renameSync`. These are file system write/move operations, so if `name` is user-controlled and unsanitized, this is a path traversal sink. Next, I traced the origin of `manifest.name`.

### Step 2: Trace the source of `manifest.name` in the upload handler (src/controllers/mcpbController.ts:83-104)
I traced back the data flow to see how the manifest is read and validated.

```ts
// src/controllers/mcpbController.ts:83-104
const manifestPath = path.join(tempExtractDir, 'manifest.json');
if (!fs.existsSync(manifestPath)) {
  throw new Error('manifest.json not found in MCPB file');
}

const manifestContent = fs.readFileSync(manifestPath, 'utf-8');
const manifest = JSON.parse(manifestContent);

// Validate required fields in manifest
if (!manifest.manifest_version) {
  throw new Error('Invalid manifest: missing manifest_version');
}
if (!manifest.name) {
  throw new Error('Invalid manifest: missing name');
}
```

Analysis: `manifest` is parsed directly from `manifest.json` inside the uploaded archive. The only check on `manifest.name` is that it is non‑empty; there is no sanitization, normalization, or allow‑list validation. Next, I confirmed the entry point for uploading MCPB files to verify user control.

### Step 3: Trace the HTTP entry point in src/routes/index.ts:297-299
I located the route that exposes the upload handler.

```ts
// src/routes/index.ts:297-299
// MCPB upload routes
router.post('/mcpb/upload', uploadMiddleware, uploadMcpbFile);
```

Analysis: The `/mcpb/upload` endpoint invokes `uploadMiddleware` and `uploadMcpbFile`, so user‑supplied uploads are the source of the manifest content. Next, I verified the upload middleware behavior.

### Step 4: Confirm the upload middleware (src/controllers/mcpbController.ts:8-38)
I inspected how the uploaded file is received and stored.

```ts
// src/controllers/mcpbController.ts:8-38
const storage = multer.diskStorage({
  destination: (_req, _file, cb) => {
    const uploadDir = path.join(process.cwd(), 'data/uploads/mcpb');
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: (_req, file, cb) => {
    const timestamp = Date.now();
    const originalName = path.parse(file.originalname).name;
    cb(null, `${originalName}-${timestamp}.mcpb`);
  },
});

const upload = multer({
  storage,
  fileFilter: (_req, file, cb) => {
    if (file.originalname.endsWith('.mcpb')) {
      cb(null, true);
    } else {
      cb(new Error('Only .mcpb files are allowed'));
    }
  },
  limits: {
    fileSize: 500 * 1024 * 1024, // 500MB limit
  },
});

export const uploadMiddleware = upload.single('mcpbFile');
```

Analysis: The upload middleware only checks file extension and size. It does not restrict or validate the contents of the archive or `manifest.name`. Therefore, `manifest.name` is user‑controlled input. Next, I checked whether any sanitization or normalization is applied before reaching the sink.

### Step 5: Verify lack of path validation on `manifest.name` in src/controllers/mcpbController.ts:92-110
I verified that no path sanitization occurs between parsing and usage.

```ts
// src/controllers/mcpbController.ts:92-110
if (!manifest.name) {
  throw new Error('Invalid manifest: missing name');
}
// ...
const finalExtractDir = path.join(path.dirname(mcpbFilePath), `server-${manifest.name}`);
cleanupOldMcpbServer(manifest.name);
```

Analysis: Before using `manifest.name` to construct a file system path, there is no `path.resolve`/`realpath` check, no use of `basename()`, and no allow‑list validation. This confirms that the path is built from untrusted input without defenses.

### Step 6: Examine cleanup behavior using the unsanitized name (src/controllers/mcpbController.ts:41-52)
I verified how `cleanupOldMcpbServer` uses the same input.

```ts
// src/controllers/mcpbController.ts:41-52
const uploadDir = path.join(process.cwd(), 'data/uploads/mcpb');
const serverPattern = `server-${serverName}`;

if (fs.existsSync(uploadDir)) {
  const files = fs.readdirSync(uploadDir);
  files.forEach((file) => {
    if (file.startsWith(serverPattern)) {
      const filePath = path.join(uploadDir, file);
      if (fs.statSync(filePath).isDirectory()) {
        fs.rmSync(filePath, { recursive: true, force: true });
      }
    }
  });
}
```

Analysis: `serverName` is used without validation, but the deletion is limited to directories already present in `uploadDir` as returned by `readdirSync`. The main traversal risk remains in constructing the path for `finalExtractDir` and the subsequent file system operations.

### Analysis Walkthrough
- Q1: Does user‑controllable input affect the file path? → **Yes**. `manifest.name` is read from the uploaded archive’s `manifest.json` and used in `path.join(...)` to build `finalExtractDir` (src/controllers/mcpbController.ts:89-110).
- Q2: Is the path normalized and validated against a base directory? → **No**. There is no `resolve`/`realpath` + `startsWith` check before `fs.mkdirSync`/`fs.renameSync` (src/controllers/mcpbController.ts:106-116).
- Q3: Is `basename()`/`getName()` used to strip directory components? → **No**. `manifest.name` is used directly in a template string (src/controllers/mcpbController.ts:106-107).
- Q4: Is there a valid allow‑list for allowed names? → **No**. Only an existence check is performed on `manifest.name` (src/controllers/mcpbController.ts:92-97).
- Q5: Is the code in a test/demo/deprecated/generated context? → **No**. This is a production controller and route (src/controllers/mcpbController.ts:64-130, src/routes/index.ts:297-299).
- → Reached leaf node: **True Positive**

## 3. Conclusion
**True Positive**

**Key evidence:**
- `manifest.name` flows directly into `finalExtractDir` and is used by `fs.mkdirSync` and `fs.renameSync` without sanitization (src/controllers/mcpbController.ts:106-116).
- `manifest.name` is parsed from `manifest.json` inside an uploaded archive, with only a non‑empty check (src/controllers/mcpbController.ts:89-97).
- The `/mcpb/upload` endpoint exposes the upload handler that processes user‑supplied archives (src/routes/index.ts:297-299).

## 4. Remediation Recommendations
- Add normalization and base directory validation before using `manifest.name` to construct `finalExtractDir` (e.g., `const resolved = path.resolve(baseDir, `server-${safeName}`); if (!resolved.startsWith(baseDir)) reject;`).
- Use `path.basename()` to strip directory components from `manifest.name` and enforce a strict character allow‑list (alphanumeric, `_`, `-`, `.`) before use.
- Consider rejecting any `manifest.name` that contains path separators or traversal sequences, and add unit tests for malicious traversal inputs.

## References
- https://github.com/samanhappy/mcphub/security/advisories/GHSA-p3h2-2j4p-p83g
- https://github.com/samanhappy/mcphub/commit/af5b013c09bb0add6b7ad9aaa5b875cf150d2a7c
- https://github.com/samanhappy/mcphub
