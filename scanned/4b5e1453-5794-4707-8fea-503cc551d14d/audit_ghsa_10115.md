# [H] SiYuan: Publish Reader Path Traversal Delete via `removeUnusedAttributeView`

## Summary
Severity: High
Advisory: GHSA-vw86-c94w-v3x4
CVE: CVE-2026-40318
CWE: CWE-24
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:L/A:H (CVSS_V3)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-vw86-c94w-v3x4
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <3.6.40.0.0-20260407035653-2f416e5253f1

## Details
## Summary

The endpoint `/api/av/removeUnusedAttributeView` is vulnerable to a **path traversal (CWE-22)** that allows an attacker to delete arbitrary `.json` files on the server.

The issue arises because user-controlled input (`id`) is directly used in filesystem path construction without validation or restriction.

> Access to this endpoint (e.g., via a Reader-role or publish context) is considered a precondition and not part of the vulnerability. The root cause is unsafe path handling.

---

## Steps To Reproduce

1. Ensure the target instance has the publish service enabled (or any valid access to the endpoint).
2. Send the following request:

```http
POST /api/av/removeUnusedAttributeView HTTP/1.1
Host: <target>
Content-Type: application/json

{
  "id": "../../../conf/conf"
}
```

3. Observe that the request is accepted.
4. The server resolves the path outside the intended directory and deletes the target file.

---

## Impact

An attacker can delete arbitrary `.json` files within the workspace directory.

This may lead to:

* Deletion of global configuration files (e.g., `conf/conf.json`)
* Loss of user data and application state
* Corruption of workspace metadata
* Persistent application instability or forced recovery

This represents a **server-side arbitrary file deletion primitive**, which can have severe impact depending on the targeted files.

---

## Technical Details

The vulnerable code constructs file paths as follows:

```go
filepath.Join(util.DataDir, "storage", "av", id+".json")
```

Because `id` is not validated, attackers can inject path traversal sequences such as `../` to escape the intended directory.

### Example payloads

* `../local` → `data/storage/local.json`
* `../../storage/outline` → `data/storage/outline.json`
* `../../../conf/conf` → `conf/conf.json`

No validation or restriction is applied to:

* input format
* path normalization
* directory boundaries

---

## Root Cause

* Untrusted user input (`id`) is directly used in filesystem path construction
* No input validation or sanitization
* No enforcement that the resolved path stays within the intended directory

---

## Remediation

1. **Validate input strictly**

   * Only allow valid Attribute View IDs
   * Reject any input containing path traversal sequences

2. **Enforce directory boundaries**

```go
base := filepath.Join(util.DataDir, "storage", "av")
absPath := filepath.Join(base, id+".json")

if !util.IsSubPath(base, absPath) {
    return error
}
```

3. **Normalize paths before use**

   * Ensure canonical paths cannot escape the base directory

4. **Add additional logical checks**

   * Verify that the target object is valid and allowed to be deleted

---

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-vw86-c94w-v3x4
- https://nvd.nist.gov/vuln/detail/CVE-2026-40318
- https://github.com/siyuan-note/siyuan
- https://github.com/siyuan-note/siyuan/releases/tag/v3.6.4
