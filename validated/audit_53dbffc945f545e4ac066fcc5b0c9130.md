### Title
Denylist-based request logging leaks non-password secrets (API keys/tokens) into debug logs - (File: core/web/router.go)

### Summary
The bug report's root cause is a *permissive-by-default validation gap*: constructor parameters that should be constrained were only checked for a narrow set of unsafe values (e.g., `royaltyFraction <= 10000` instead of a sane cap), letting out-of-scope values slip through unnoticed. The equivalent pattern in this codebase is `core/web/router.go`'s request-logging sanitizer, which redacts request bodies/queries using a hardcoded **denylist** of field names rather than validating/allowlisting what is safe to log. Any sensitive field whose name isn't `password`-like is logged in cleartext.

### Finding Description
`loggerFunc` is installed as global Gin middleware and logs every incoming request body and query string at debug level: [1](#0-0) 

The sanitization it relies on, `readSanitizedJSON`/`redact`, only redacts a field if its key matches (or contains) `"password"`: [2](#0-1) 

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
```

This mirrors the audited bug class exactly: instead of validating that only *safe* values/fields are allowed to flow through (allowlist), the code assumes everything is safe except a small, explicitly enumerated set of unsafe cases (denylist). Just as an unconstrained `royaltyFraction` let the deployer set an unintended 100% fee, an unconstrained logging sanitizer lets any JSON field not literally containing "password" (e.g. `secret`, `apiSecret`, `accessKey`, `token`, `privateKey`, or nested objects containing such fields) be written verbatim into node logs. `readSanitizedJSON` also only inspects **top-level** keys — nested JSON objects/arrays are copied through unfiltered regardless of key name, compounding the gap.

### Impact Explanation
Node operators/administrators who read debug logs (or ship them to a centralized logging system) could inadvertently capture credentials from any endpoint whose request payload includes a sensitively-named field that doesn't contain "password". This is a genuine secret-disclosure risk class (matches the "secret redaction" category), though the severity depends on which endpoints accept such fields — this is a defense-in-depth/logging-hygiene gap rather than a directly exploitable authentication bypass. I could not verify a concrete production endpoint whose JSON body currently contains an unredacted secret-bearing field name (e.g. `secret`, `token`, `apiKey`) other than password-typed ones within the scope I searched (bridge, session, external-initiator, keys controllers use `password`-named fields, which are caught). This should be treated as **Low/Medium** severity absent a confirmed concrete leaking endpoint.

### Likelihood Explanation
Likelihood is moderate: it requires (1) debug-level logging enabled, and (2) an existing or future request body/query parameter with a sensitive but non-"password" name reaching this middleware (which is global to the Gin router, so it applies to nearly all `/v2/*` endpoints). Given the denylist is small and only string-contains "password", any new field addition (e.g., `secret`, `token`) is not proactively protected — this is a maintenance/regression risk more than an immediately provable exploit against current wired endpoints.

### Recommendation
1. Replace the denylist approach with an allowlist, or at minimum broaden the denylist to include common secret-indicating substrings: `secret`, `token`, `apikey`, `key`, `credential`, `auth`.
2. Make `readSanitizedJSON` recursively sanitize nested objects/arrays, not just top-level keys.
3. Consider disabling full body/query logging by default at debug level, or hashing/truncating instead of raw-echoing unknown fields.

### Proof of Concept
Not directly demonstrable without a concrete endpoint accepting a non-"password" secret field in scope; conceptually: `POST` any JSON body containing `{"apiSecret": "supersecret"}` to any `/v2/*` route with debug logging enabled — `readSanitizedJSON` will pass `apiSecret` through unredacted into the log line produced by `loggerFunc` at [3](#0-2) .

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

**File:** core/web/router.go (L608-658)
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
