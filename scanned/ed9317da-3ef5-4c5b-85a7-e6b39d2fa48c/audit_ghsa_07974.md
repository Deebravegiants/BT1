# [H] Gogs vulnerable to arbitrary file deletion via Path Traversal in wiki page update

## Summary
Severity: High
Advisory: GHSA-jp7c-wj6q-3qf2
CVE: CVE-2026-24135
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-02-06
Source: https://github.com/advisories/GHSA-jp7c-wj6q-3qf2
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.13.4

## Details
### Summary
A Path Traversal vulnerability exists in the `updateWikiPage` function of Gogs. The vulnerability allows an authenticated user with write access to a repository's wiki to delete arbitrary files on the server by manipulating the `old_title` parameter in the wiki editing form.

### Vulnerability Deatils
The vulnerability is located in `internal/database/wiki.go`. When updating a wiki page, the application accepts an `old_title` parameter to identify the potential rename operation. This parameter is used directly in `path.Join` and `os.Remove` without proper sanitization.

Code snippet from `internal/database/wiki.go`:
```go
// Line 114
os.Remove(path.Join(localPath, oldTitle+".md"))
```

If an attacker provides a path traversal sequence (e.g., `../../../../target`) as `old_title`, the `os.Remove` function will resolve the path relative to the wiki's local directory and delete the target file. The vulnerability is limited to deleting files that end with `.md` (due to the appended extension), but depending on the filesystem and specific `path.Join` behavior, or if critical `.md` files exist (e.g. documentation, other wikis), the impact is significant. Additionally, in some contexts, the extension might be bypassed or ignored.

### Impact
- **Denial of Service**: Deletion of critical configuration files or data (if they match the extension or via other tricks).
- **Data Loss**: Deletion of other users' wiki pages or documentation.

### Remediation
Sanitize the `oldTitle` parameter using `ToWikiPageName` (or `path.Clean` and basename validation) before using it in file operations, similar to how the new `title` is currently handled.

```go
// Recommended Fix
if oldTitle != "" {
    oldTitle = ToWikiPageName(oldTitle)
}
```

### Reproduction Steps
1.  Log in to Gogs as a user with write access to a repository wiki.
2.  Intercept the `POST` request to `/repo/wiki/edit`.
3.  Modify the `old_title` parameter to `../../../../tmp/target_file`.
4.  Submit the request.
5.  Observe that `/tmp/target_file.md` is deleted from the server.

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-jp7c-wj6q-3qf2
- https://nvd.nist.gov/vuln/detail/CVE-2026-24135
- https://github.com/gogs/gogs
