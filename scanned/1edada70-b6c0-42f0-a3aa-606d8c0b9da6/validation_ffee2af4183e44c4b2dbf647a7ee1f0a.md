## Analog Found

### Title
Sandboxie-style secret exposure via side channel — key import/export passwords sent as URL query parameters instead of request body - (File: core/web/keys_controller.go)

### Summary
The CVE-2025-54422 root cause is that Sandboxie transmits old/new passwords through a channel that is readable by other local actors (command-line arguments) rather than through a protected channel. Chainlink's key-management HTTP endpoints exhibit the same bug class: the old/new passwords used to import/export cryptographic keys are transmitted as **URL query-string parameters** (`?oldpassword=...`, `?newpassword=...`) instead of inside the encrypted/TLS-protected JSON request body payload proper to the operation, making them susceptible to capture by any component that has visibility into request URLs — access logs, reverse proxies, CDNs, browser history, and HTTP `Referer` headers — none of which need the caller's own session/API credentials to observe them.

### Finding Description
`keysController.Import` and `keysController.Export` read the encryption password directly from the query string: [1](#0-0) [2](#0-1) 

The CLI clients construct these requests by appending the (already-read-from-file) plaintext password to the URL: [3](#0-2) 

This same pattern is duplicated across every key type's controller/CLI pair — `core/web/csa_keys_controller.go`, `core/web/eth_keys_controller.go`, `core/web/ocr_keys_controller.go`, `core/web/ocr2_keys_controller.go`, `core/web/p2p_keys_controller.go`, `core/web/vrf_keys_controller.go`, and their corresponding `core/cmd/*_keys_commands.go` files (confirmed via the `oldpassword|newpassword` grep matches).

The application itself is aware that "password"-named parameters are sensitive: its internal request logger explicitly redacts them before writing to its own debug logs — [4](#0-3) 
— but this redaction only covers Chainlink's own structured debug log line. It does nothing to prevent the plaintext password from appearing in:
- Reverse-proxy/load-balancer access logs (nginx, ALB, Cloudflare, etc.) sitting in front of the node, which by default log the full request URI including query string.
- Browser history/autocomplete if these requests are ever issued from a browser-based tool.
- `Referer` headers sent to any third-party resource loaded by a page that triggered the request.

This mirrors the Sandboxie root cause precisely: a secret needed only by the local privileged process is instead placed on a transport surface (CLI args / URL query string) that is visible to unrelated, lower-privilege observers (any process on the box / any log-consuming or proxying entity), bypassing the protections normally afforded to request bodies.

### Impact Explanation
An entity with access to HTTP infrastructure logs, monitoring pipelines, or intermediary proxies — none of which require possessing the node operator's session cookie or API token — can recover the plaintext password used to encrypt a Chainlink key (ETH, CSA, OCR, OCR2, P2P, VRF). Because these passwords are frequently reused as node account/master passwords or key-encryption passphrases, disclosure can lead to offline decryption of exported key material and compromise of node keys governing fund movement and job signing.

### Likelihood Explanation
Any operational chainlink deployment behind a reverse proxy, API gateway, or centralized logging/observability stack (a near-universal production pattern) will, by default, capture full request URLs including query strings for every `/v2/keys/*/import` and `/v2/keys/*/export` call. No special configuration or attacker action is needed beyond normal operational logging — the exposure is passive and automatic, matching the "no privilege required" character of the original CVE.

### Recommendation
Move `oldpassword`/`newpassword` (and any similarly sensitive parameters) out of the URL query string and into the JSON request body for all `Import`/`Export` key controller endpoints (`core/web/keys_controller.go` and its per-key-type counterparts), updating the corresponding CLI clients (`core/cmd/keys_commands.go`, etc.) to POST the password in the body rather than appending it to the request path. Additionally, ensure any documentation/scripts warning operators about proxy/log configuration for these endpoints in the interim.

### Proof of Concept
1. Configure a Chainlink node behind a standard reverse proxy (e.g., nginx) with default access-log format (`$request_uri`).
2. As an authenticated node operator, run `chainlink keys eth import <path> --old-password pw.txt`, which triggers:
`POST /v2/keys/eth/import?oldpassword=<PLAINTEXT_PASSWORD>` — see [3](#0-2) .
3. Inspect the reverse proxy's access log — the plaintext password appears in the logged request line, retrievable by anyone with read access to that log file (e.g., a log-shipping agent, a different unprivileged system user, or a misconfigured log aggregation dashboard), without ever needing the operator's session or API credentials.

**Caveat/uncertainty:** I was not able to fully verify the exact role-gating (e.g., whether Admin-only) applied to `/v2/keys/*` routes in `core/web/router.go` before running out of tool iterations, since the relevant route-registration section wasn't retrieved in full. This does not change the core defect (secret placed in URL query string), but the precise authorization level required to *trigger* the leaking request should be confirmed by a follow-up review of `core/web/router.go`'s key route group registration.

### Citations

**File:** core/web/keys_controller.go (L114-136)
```go
func (kc *keysController[K, R]) Import(c *gin.Context) {
	defer kc.lggr.ErrorIfFn(c.Request.Body.Close, "Error closing Import request body")
	ctx := c.Request.Context()

	bytes, err := io.ReadAll(c.Request.Body)
	if err != nil {
		jsonAPIError(c, http.StatusBadRequest, err)
		return
	}
	oldPassword := c.Query("oldpassword")
	key, err := kc.ks.Import(ctx, bytes, oldPassword)
	if err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	kc.auditLogger.Audit(audit.KeyImported, map[string]any{
		"type": kc.typ,
		"id":   key.ID(),
	})

	jsonAPIResponse(c, kc.newResource(key), kc.resourceName)
}
```

**File:** core/web/keys_controller.go (L138-155)
```go
func (kc *keysController[K, R]) Export(c *gin.Context) {
	defer kc.lggr.ErrorIfFn(c.Request.Body.Close, "Error closing Export request body")

	keyID := c.Param("ID")
	newPassword := c.Query("newpassword")
	bytes, err := kc.ks.Export(keyID, newPassword)
	if err != nil {
		jsonAPIError(c, http.StatusInternalServerError, err)
		return
	}

	kc.auditLogger.Audit(audit.KeyExported, map[string]any{
		"type": kc.typ,
		"id":   keyID,
	})

	c.Data(http.StatusOK, MediaType, bytes)
}
```

**File:** core/cmd/keys_commands.go (L185-196)
```go
	filepath := c.Args().Get(0)
	keyJSON, err := os.ReadFile(filepath)
	if err != nil {
		return cli.errorOut(err)
	}

	normalizedPassword := normalizePassword(string(oldPassword))
	resp, err := cli.HTTP.Post(cli.ctx(), cli.path+"/import?oldpassword="+normalizedPassword, bytes.NewReader(keyJSON))
	if err != nil {
		return cli.errorOut(err)
	}
	defer func() {
```

**File:** core/web/router.go (L631-658)
```go
func redact(values url.Values) string {
	cleaned := url.Values{}
	for k, v := range values {
		if isBlacklisted(k) {
			cleaned[k] = []string{"REDACTED"}
			continue
		}
		cleaned[k] = v
	}
	return cleaned.Encode()
}

// NOTE: keys must be in lowercase for case insensitive match
var blacklist = map[string]struct{}{
	"password":             {},
	"newpassword":          {},
	"oldpassword":          {},
	"current_password":     {},
	"new_account_password": {},
}

func isBlacklisted(k string) bool {
	lk := strings.ToLower(k)
	if _, ok := blacklist[lk]; ok || strings.Contains(lk, "password") {
		return true
	}
	return false
}
```
