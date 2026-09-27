# [M] SiYuan: Absolute filesystem path and OS username disclosure via resolveAssetPath

## Summary
Severity: Medium
Advisory: GHSA-jv8v-xq2h-657v
Aliases: CVE-2026-72802, GO-2026-6398
Ecosystem: Go
Published: 2026-09-03
Source: https://osv.dev/vulnerability/GHSA-jv8v-xq2h-657v
Type: osv

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0 <0.0.0-20260724095509-eee3410aa131

## Details
**CVE:** This vulnerability corresponds to [CVE-2026-72802](https://nvd.nist.gov/vuln/detail/CVE-2026-72802).

### Summary

`POST /api/asset/resolveAssetPath` returns the resolved **absolute** filesystem path of an asset, unmodified. The route is `CheckAuth`-only, so it is reachable by the publish `RoleReader` token and by the anonymous account when `Publish.Auth.Enable` is `false`. An anonymous reader who knows any asset's relative path trivially harvested from an `<img src="assets/…">` in any published document receives the server's absolute workspace path, disclosing the operating-system username and the installation layout.

### Details

```go
// kernel/api/asset.go: resolveAssetPath
p, err := model.GetAssetAbsPathInBox(path, "")   // boxID="" → absolute workspace path
...
ret.Data = p                                     // returned raw, no stripping
```

`GetAssetAbsPathInBox(path, "")` resolves under `util.DataDir` / `util.WorkspaceDir`, producing a full host path such as `C:\Users\<username>\SiYuan\data\assets\foo.png` or `/home/<user>/…`. The handler returns it directly with no redaction and no publish-scope check.

**This is data the project already treats as sensitive.** `getConf` explicitly zeroes `System.WorkspaceDir`, `AppDir`, `ConfDir`, `DataDir`, and `HomeDir` when `util.IsBrowserRequest(c)`, a change made specifically to avoid leaking the username (issue #17410). `resolveAssetPath` performs no equivalent stripping, so it re-exposes precisely the values `getConf` was patched to hide.

**Related unfiltered siblings** in the same file, also `CheckAuth`-only with no publish scoping:
- `getMissingAssets`: workspace-wide list of missing asset references
- `getUnusedAssets`: every unused asset filename in the assets directory

Both return asset inventory spanning all documents, including publish-forbidden ones.

Verified at `origin/master`: `resolveAssetPath` returns the absolute path with no redaction, `getConf` contains the `IsBrowserRequest` stripping; all three routes are registered `CheckAuth` without `CheckAdminRole`.

### Proof of Concept

Precondition: publish mode enabled (default port 6808); anonymous when `Publish.Auth.Enable` is `false`, otherwise any publish reader account.

**1. Harvest an asset path**: open any published document and read a relative asset path from its markup, e.g. `assets/foo-20260101120000-abcdefg.png`.

**2. Resolve it as an anonymous reader:**
```
POST http://127.0.0.1:6808/api/asset/resolveAssetPath
{"path":"assets/foo-20260101120000-abcdefg.png"}
```

**3. Result:** the response returns the absolute host path, e.g.
`C:\Users\<username>\SiYuan\data\assets\foo-...png` disclosing the OS username and the full workspace/installation layout.

**Control:** `getConf` from the same anonymous session returns `WorkspaceDir`/`DataDir`/`HomeDir` blanked, confirming the project intends these values to be withheld from browser requests.

**Related:**
```
POST http://127.0.0.1:6808/api/asset/getUnusedAssets   {}
POST http://127.0.0.1:6808/api/asset/getMissingAssets  {}
```
Return workspace-wide asset inventory with no publish scoping.

### Impact

An anonymous reader (publish mode with auth disabled) or any publish `RoleReader` obtains the server's absolute workspace path, which typically embeds the OS username, plus the installation directory layout. This is useful for targeting subsequent attacks (path construction, user enumeration, social engineering) and directly contradicts the redaction the project applies in `getConf`. The related endpoints additionally disclose workspace-wide asset inventory, including assets referenced only by publish-forbidden documents. Confidentiality-only.

### Suggested fix

Apply the same redaction `getConf` uses: for browser/reader requests, return the asset path relative to the workspace root rather than the absolute host path (or omit it entirely). Add publish-access scoping to `getUnusedAssets` and `getMissingAssets` so their results are limited to documents the caller may see.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-jv8v-xq2h-657v
- https://nvd.nist.gov/vuln/detail/CVE-2026-72802
- https://github.com/siyuan-note/siyuan/commit/eee3410aa131b76f1bd72e933d484cf1ece77e88
- https://github.com/siyuan-note/siyuan
- https://www.vulncheck.com/advisories/siyuan-before-information-disclosure-via-resolveassetpath
