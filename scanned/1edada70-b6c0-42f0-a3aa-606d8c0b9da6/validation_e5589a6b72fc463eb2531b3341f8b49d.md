### Title
Field-name-based blacklist in HTTP request logging middleware can leak secrets (bridge secrets, API tokens, bridge confirmations, external-initiator secrets) into node logs - ([File: core/web/router.go])

### Summary
Cilium's `cilium-bugtool` leaked TLS keys/certs and Kafka API keys because debug output was collected without a comprehensive redaction of sensitive fields. Chainlink's Gin request-logging middleware has an analogous flaw: it redacts request bodies/query params using a hardcoded, substring-based denylist that only matches variants of the word `"password"`, rather than allowlisting only known-safe fields.

### Finding Description
The `loggerFunc` middleware reads the full request body and query string for every API request and logs them at debug level via `readBody`/`redact`, which call `readSanitizedJSON`/`redact`. Both rely on `isBlacklisted`, which only redacts keys equal to a small fixed set (`password`, `newpassword`, `oldpassword`, `current_password`, `new_account_password`) or containing the substring `"password"`. [1](#0-0) 

Any request field whose name doesn't happen to contain "password" is logged verbatim in cleartext at debug level, including into disk-based debug logs (enabled by default per `LOG_FILE_MAX_SIZE`, intended for node operators to send to the Chainlink team for support — the same "debug artifact shared for troubleshooting" pattern that caused the Cilium leak). [2](#0-1) 

Examples of sensitive fields that are NOT covered by the denylist:
- External Initiator creation, which returns/accepts `IncomingSecret`/`OutgoingSecret` fields used to authenticate initiator callbacks (`core/web/external_initiators_controller.go`, binds via `BindJSON`).
- Bridge type creation/update, which includes a `Confirmations`/`OutgoingToken`-style secret used to authenticate bridge adapter calls (`core/web/bridge_types_controller.go`).
- Session/API-token related requests bound via `BindJSON` in `core/web/sessions_controller.go` and `core/web/user_controller.go`, where token/secret-bearing fields other than "password" would pass through unredacted.

Because `isBlacklisted` is a denylist keyed on a fixed vocabulary rather than an allowlist of safe fields, any newly-added or differently-named secret field (e.g., `secret`, `token`, `apiKey`, `privateKey`) is logged in the clear by default — mirroring the root cause of GHSA-wh78-7948-358j, where the debug/diagnostic collection path failed to comprehensively strip secret material.

### Impact Explanation
An operator (or anyone with access to node logs/disk log files, which are world-readable by default enablement of disk logging) can recover plaintext secrets such as external-initiator `IncomingSecret`/`OutgoingSecret` or bridge secrets, which are used to authenticate cross-service calls into and out of the node. Disclosure of these secrets enables request impersonation of the bridge/external-initiator channel and unauthorized triggering of job runs — matching the "secret/key disclosure" and "unauthorized job run" categories of acceptable impact.

### Likelihood Explanation
Debug-level HTTP logging is on by default whenever `Log.Level = debug` (a common operator configuration for troubleshooting) and disk-based debug logging is enabled by default whenever `Log.File.MaxSize` is set above zero, so this leak occurs automatically during normal, unprivileged API traffic (e.g., a bridge or external-initiator creation call) without requiring any special trigger — likelihood is moderate-to-high, gated on the node operator enabling debug logging, which is a common support/debugging workflow (directly parallel to running `cilium-bugtool`).

### Recommendation
Replace the denylist-based `blacklist`/`isBlacklisted` approach in `core/web/router.go` with an explicit allowlist of loggable field names, or redact request/response bodies entirely for endpoints known to carry secret material (external initiators, bridges, sessions/API tokens). At minimum, extend the denylist to include `secret`, `token`, `key`, `incomingsecret`, `outgoingsecret`, and similar substrings, and audit all `BindJSON`/`ShouldBindJSON` request structs for secret-bearing fields.

### Proof of Concept
1. Set `Log.Level = 'debug'` (and optionally enable disk logging via `Log.File.Dir`).
2. As any authenticated (or, for external initiator webhook, low-privilege) client, call `POST /v2/external_initiators` to create an external initiator; the response contains `OutgoingSecret`/`IncomingSecret`.
3. Inspect the node's debug logs (`lggr.Debugw` output in `loggerFunc`, `core/web/router.go` lines 556-567): the request/response body containing these secret fields is present in cleartext because `isBlacklisted` (lines 652-658) does not match on `secret`.
4. Anyone with read access to the node's log output (support bundle, log aggregator, etc.) can extract the initiator secret and forge authenticated webhook calls to the node.

### Citations

**File:** core/web/router.go (L556-567)
```go
		lggr.Debugw(fmt.Sprintf("%s %s", c.Request.Method, c.Request.URL.Path),
			"method", c.Request.Method,
			"status", c.Writer.Status(),
			"path", c.Request.URL.Path,
			"ginPath", c.FullPath(),
			"query", redact(c.Request.URL.Query()),
			"body", readBody(rdr, lggr),
			"clientIP", c.ClientIP(),
			"errors", c.Errors.String(),
			"servedAt", end.Format("2006-01-02 15:04:05"),
			"latency", fmt.Sprintf("%v", end.Sub(start)),
		)
```

**File:** core/web/router.go (L643-658)
```go
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
