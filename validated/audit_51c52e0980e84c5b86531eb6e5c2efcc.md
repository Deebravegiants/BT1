### Title
Debug-level request logging middleware redacts only "password"-named fields, leaking other sensitive request-body values (secrets/tokens/keys) to node logs - (File: core/web/router.go)

### Summary
The bug class in the external report is a missing-accounting defect: a security-relevant list (`tokensIn`) fails to enumerate a value that must be tracked, causing unaccounted funds. The Chainlink node's HTTP request-logging middleware exhibits the same class of defect: the redaction "blacklist" used before logging request bodies enumerates only password-like keys, so any other sensitive field name in a JSON request body is logged in plaintext at Debug level.

### Finding Description
Every request that hits the Chainlink node's Gin router is wrapped by `loggerFunc`, which reads the full raw request body, runs it through `readBody`/`readSanitizedJSON`, and logs the result: [1](#0-0) 

`readSanitizedJSON` walks the top-level JSON keys of the body and only redacts a key if `isBlacklisted` returns true: [2](#0-1) 

The blacklist itself is a hard-coded, incomplete enumeration:
```go
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
``` [3](#0-2) 

This is structurally the same defect as the H-01 report: a list meant to comprehensively account for a class of sensitive values (there: reward tokens received; here: sensitive field names to redact) only covers a subset of the class, so anything outside that subset — for example, keys such as `secret`, `apiKey`, `accessKey`, `token`, `privateKey`, or `mnemonic` (field names that do exist elsewhere in the codebase, e.g. `ExternalInitiatorAuthentication.Secret`/`OutgoingToken`, and are plausible request-body field names for similarly-shaped write endpoints) — falls through unredacted. The same gap applies to `redact(url.Values)` for query parameters, which uses the identical `isBlacklisted` check: [4](#0-3) 

### Impact Explanation
Because `loggerFunc` is a router-wide middleware applied to (unauthenticated as well as authenticated) HTTP endpoints, any request body field whose name does not literally contain "password" is written verbatim into the node's Debug logs. If any current or future admin/API endpoint accepts a secret, token, or key under a non-"password" field name in its request body, that value is persisted into node logs, which are frequently shipped to third-party log aggregators, ops dashboards, or support bundles — a straightforward secret-disclosure vector once Debug logging is enabled (a common state in non-production/staging deployments and during troubleshooting).

### Likelihood Explanation
This is triggered automatically and unconditionally by the router middleware for every matching request — no attacker action beyond sending a normal request is required (an unprivileged client can trigger the code path for any endpoint reachable pre-auth, such as login, and any authenticated client triggers it for every write request). The likelihood of a concrete leak depends only on whether some accepted body field is named outside the fixed password-only blacklist, which is highly plausible given the variety of secret-bearing resources in the API (external initiators, API tokens, credentials) and is a design defect independent of any specific endpoint.

### Recommendation
Broaden `isBlacklisted` from an exact/substring match on "password" variants to a substring match against a superset of sensitive-term keywords (`secret`, `token`, `key`, `credential`, `apikey`, `accesskey`, `mnemonic`, `authorization`, etc.), or switch to an allowlist model where only explicitly-approved fields are logged and everything else is redacted by default. Apply the same fix to both `readSanitizedJSON` (body) and `redact` (query params).

### Proof of Concept
1. Enable Debug-level logging on a running Chainlink node.
2. Send any authenticated (or, for pre-auth endpoints, unauthenticated) HTTP request whose JSON body contains a sensitive field under a key that does not contain the substring "password" (e.g. `{"apiKey": "supersecretvalue"}` or `{"token": "supersecretvalue"}`).
3. Observe the node's Debug log line emitted by `loggerFunc` (`"body"` field) contains the sensitive value unredacted, because `isBlacklisted` only matches `password`/`newpassword`/`oldpassword`/`current_password`/`new_account_password`.

### Citations

**File:** core/web/router.go (L534-568)
```go
func loggerFunc(lggr logger.Logger) gin.HandlerFunc {
	return func(c *gin.Context) {
		buf, err := io.ReadAll(c.Request.Body)
		if err != nil {
			lggr.Error("Web request log error: ", err.Error())
			// Implicitly relies on limits.RequestSizeLimiter
			// overriding of c.Request.Body to abort gin's Context
			// inside io.ReadAll.
			// Functions as we would like, but horrible from an architecture
			// and design pattern perspective.
			if !c.IsAborted() {
				c.AbortWithStatus(http.StatusBadRequest)
			}
			return
		}
		rdr := bytes.NewBuffer(buf)
		c.Request.Body = io.NopCloser(bytes.NewBuffer(buf))

		start := time.Now()
		c.Next()
		end := time.Now()

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
	}
```

**File:** core/web/router.go (L608-629)
```go
func readSanitizedJSON(buf *bytes.Buffer) (string, error) {
	var dst map[string]any
	err := json.Unmarshal(buf.Bytes(), &dst)
	if err != nil {
		return "", err
	}

	cleaned := map[string]any{}
	for k, v := range dst {
		if isBlacklisted(k) {
			cleaned[k] = "*REDACTED*"
			continue
		}
		cleaned[k] = v
	}

	b, err := json.Marshal(cleaned)
	if err != nil {
		return "", err
	}
	return string(b), err
}
```

**File:** core/web/router.go (L631-641)
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
