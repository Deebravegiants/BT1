# [M] Vikjuna Bypasses Webhook SSRF Protections During OpenID Connect Avatar Download 

## Summary
Severity: Medium
Advisory: GHSA-g9xj-752q-xh63
CVE: CVE-2026-33679
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:L (CVSS_V3)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-g9xj-752q-xh63
Type: github-advisory

## Affected
- Go: `code.vikunja.io/api` — affected >=0 <2.2.1

## Details
## Summary

The `DownloadImage` function in `pkg/utils/avatar.go` uses a bare `http.Client{}` with no SSRF protection when downloading user avatar images from the OpenID Connect `picture` claim URL. An attacker who controls their OIDC profile picture URL can force the Vikunja server to make HTTP GET requests to arbitrary internal or cloud metadata endpoints. This bypasses the SSRF protections that are correctly applied to the webhook system.

## Details

When a user authenticates via OpenID Connect, Vikunja extracts the `picture` claim from the ID token or UserInfo endpoint and passes it to `syncUserAvatarFromOpenID`, which calls `utils.DownloadImage` with the attacker-controlled URL:

**Claim extraction** (`pkg/modules/auth/openid/openid.go:70-78`):
```go
type claims struct {
	Email              string                   `json:"email"`
	Name               string                   `json:"name"`
	PreferredUsername   string                   `json:"preferred_username"`
	Nickname           string                   `json:"nickname"`
	VikunjaGroups      []map[string]interface{} `json:"vikunja_groups"`
	Picture            string                   `json:"picture"`
	// ...
}
```

**Avatar sync trigger** (`pkg/modules/auth/openid/openid.go:348-352`):
```go
// Try sync avatar if available
err = syncUserAvatarFromOpenID(s, u, cl.Picture)
if err != nil {
	log.Errorf("Error syncing avatar for user %s: %v", u.Username, err)
}
```

**Vulnerable download** (`pkg/utils/avatar.go:94-115`):
```go
func DownloadImage(url string) ([]byte, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
	defer cancel()

	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create HTTP request: %w", err)
	}

	resp, err := (&http.Client{}).Do(req)  // No SSRF protection
	// ...
	return io.ReadAll(resp.Body)  // No size limit
}
```

In contrast, the webhook system correctly applies SSRF protection (`pkg/models/webhooks.go:306-310`):
```go
if !config.WebhooksAllowNonRoutableIPs.GetBool() {
	guardian := ssrf.New(ssrf.WithAnyPort())
	transport.DialContext = (&net.Dialer{
		Control: guardian.Safe,
	}).DialContext
}
```

The avatar download path has none of this protection. There is no URL scheme validation, no IP address filtering, and no response body size limit.

## PoC

**Prerequisites:** A Vikunja instance with OpenID Connect configured (e.g., Keycloak, Authentik). Attacker has an account on the OIDC provider.

**Step 1:** Set up a listener to observe incoming requests:
```bash
# On attacker-controlled server or internal service
nc -lvp 8888
```

**Step 2:** In the OIDC provider (e.g., Keycloak admin), update the attacker's user profile picture URL to an internal address:
```
http://169.254.169.254/latest/meta-data/iam/security-credentials/
```
Or to probe internal services:
```
http://internal-service:8888/admin
```

**Step 3:** Log in to Vikunja via the OIDC provider. After the callback completes, the Vikunja server will make a GET request from its own network context to the URL set in the picture claim.

**Step 4:** Observe the request arriving at the internal endpoint or listener. The request originates from the Vikunja server's IP, bypassing any network-level access controls that allow Vikunja server traffic.

**Cloud metadata example (AWS):**
```
# Set picture URL to:
http://169.254.169.254/latest/meta-data/iam/security-credentials/

# Vikunja server makes GET to this URL from its own network context
# The response is read into memory (io.ReadAll) before image.Decode fails
# The HTTP request itself reaches the metadata service
```

## Impact

- **Cloud metadata access:** Attacker can reach cloud instance metadata services (AWS IMDSv1 at `169.254.169.254`, GCP, Azure equivalents) from the Vikunja server's network position, potentially leaking IAM credentials, instance identity tokens, and configuration data.
- **Internal network reconnaissance:** Port scanning and service discovery of internal hosts reachable from the Vikunja server by observing response timing and error messages.
- **Internal service interaction:** Any internal service that acts on GET requests (cache purges, status endpoints, admin panels) can be triggered.
- **Memory pressure:** The `io.ReadAll` call with no size limit means pointing the URL at a large resource could cause memory exhaustion on the Vikunja server, though the 3-second timeout partially mitigates this.
- **Repeated exploitation:** The SSRF triggers on every OIDC login, allowing the attacker to iterate through different internal URLs by updating their OIDC profile between logins.

## Recommended Fix

Apply the same SSRF protection used in webhooks to `DownloadImage`, and add a response body size limit:

```go
// pkg/utils/avatar.go
import (
	"net"
	"code.dny.dev/ssrf"
)

func DownloadImage(url string) ([]byte, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
	defer cancel()

	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return nil, fmt.Errorf("failed to create HTTP request: %w", err)
	}

	// SSRF protection: block requests to non-globally-routable IPs
	guardian := ssrf.New(ssrf.WithAnyPort())
	client := &http.Client{
		Transport: &http.Transport{
			DialContext: (&net.Dialer{
				Control: guardian.Safe,
			}).DialContext,
		},
	}

	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to download image: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("failed to download image, status code: %d", resp.StatusCode)
	}

	// Limit response body to 10MB to prevent memory exhaustion
	const maxAvatarSize = 10 * 1024 * 1024
	return io.ReadAll(io.LimitReader(resp.Body, maxAvatarSize))
}
```

## References
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-g9xj-752q-xh63
- https://nvd.nist.gov/vuln/detail/CVE-2026-33679
- https://github.com/go-vikunja/vikunja/commit/363aa6642352b08fc8bc6aaff2f3a550393af1cf
- https://github.com/go-vikunja/vikunja
- https://pkg.go.dev/vuln/GO-2026-4852
- https://vikunja.io/changelog/vikunja-v2.2.2-was-released
