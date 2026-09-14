### Title
Incomplete secret redaction in Web API request logging causes plaintext disclosure of sensitive parameters to disk logs - (File: `core/web/router.go`)

### Summary
Chainlink's gin request logger (`loggerFunc`) writes every inbound Web API request body to the node's Debug-level log stream, applying a redaction filter (`isBlacklisted`/`blacklist`) that only masks fields whose key name contains the substring `"password"`. Any other sensitive value submitted in a JSON request body (tokens, client secrets, pre-shared keys, etc.) is captured verbatim into the node's on-disk log files, mirroring the root cause of CVE-2022-27195 (Jenkins Parameterized Trigger Plugin capturing sensitive build parameters unencrypted into `build.xml`, viewable by anyone with filesystem access).

### Finding Description
`loggerFunc` reads the full request body and logs it via `readBody`, which calls `readSanitizedJSON`: [1](#0-0) 

`readSanitizedJSON` and `redact` only redact keys that match the hardcoded `blacklist` (`password`, `newpassword`, `oldpassword`, `current_password`, `new_account_password`) or that contain the substring `"password"`: [2](#0-1) 

This is the same class of bug as the Jenkins CVE: values are "captured" from user-supplied request data and durably persisted (to the node's log files on disk) without encryption or adequate redaction, based on an incomplete allow/deny-list of "sensitive" field names rather than a security-reviewed schema of secret fields. Any request body field not literally named with the word "password" — for example a `secret`, `token`, `clientSecret`, `psk`, or similar credential value submitted by a client to a Web API endpoint — is written unredacted into the Debug log stream and persisted to disk when file-based logging is enabled (`Log.File`, `DebugLogsToDisk`): [3](#0-2) 

This log capture applies indiscriminately to all Web API routes it wraps, regardless of the caller's role, so any authenticated (even minimally privileged) API client whose request body contains a non-`password`-named secret will have that secret persisted unencrypted to the node operator's log files — exactly analogous to Jenkins storing password-parameter values unencrypted in `build.xml`.

### Impact Explanation
Anyone with read access to the Chainlink node's file system (log directory) can recover plaintext secret values submitted via the Web API that don't happen to have "password" in their JSON key name. This is a secret-disclosure vector consistent with the CVE's impact classification (Confidentiality: High, no Integrity/Availability impact), and the trigger requires no special network position — merely submitting a request containing a sensitive field to the node's HTTP API while Debug-level (or file-based debug) logging is active.

### Likelihood Explanation
The gap is deterministic and not proximity- or timing-dependent: it triggers whenever (a) Debug-level logging is enabled (or debug logs are persisted to disk via `Log.File`) and (b) a request body contains a sensitive field whose key does not literally contain "password". Given the router applies this logger broadly, the likelihood of at least one such field existing among the Web API surface is non-trivial, though I could not enumerate within the indexed code a specific production endpoint whose JSON body carries a named secret field other than "password" (e.g., I found no `json:"secret"`/`json:"token"`/`json:"psk"` request-body tags under `core/web/`), so likelihood is somewhat uncertain and depends on unindexed endpoints or future/administrative fields.

### Recommendation
- Replace the substring/keyword blacklist approach with an explicit allow-list of loggable fields, or use a struct-tag-based redaction (`json:"-"` / a `Sensitive` marker) enforced at the type level for any request/response DTO carrying credentials.
- Disable full request-body debug logging by default, or truncate/hash bodies before persisting to disk.
- Broaden `blacklist` in `isBlacklisted` (`core/web/router.go`) to also match `secret`, `token`, `key`, `psk`, `credential`, etc., as a stopgap.

### Proof of Concept
1. Enable file-based debug logging (`Log.Level = 'debug'`, `Log.File.Dir` set) as in the config used by `testdata/scripts/node/validate/disk-based-logging-disabled.txtar`.
2. Send any authenticated Web API request whose JSON body contains a sensitive field not named with "password" (e.g., `{"apiSecret": "sk-verysecretvalue"}`) to a route wrapped by `loggerFunc`.
3. Inspect the node's log file (`LogsFile()` in `core/logger/logger.go`); the field and its raw value will appear unredacted in the `"body"` log entry, since `isBlacklisted` in `core/web/router.go` only matches "password"-like keys.

Note: I was unable to positively confirm, within the indexed portion of the repo, a concrete production JSON request field carrying a real credential value that both (a) reaches `loggerFunc` and (b) doesn't contain "password" in its key name — this weakens certainty about real-world reachability/impact and should be verified with full repo access.

### Citations

**File:** core/web/router.go (L534-567)
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

**File:** core/logger/logger.go (L214-217)
```go
// DebugLogsToDisk returns whether debug logs should be stored in disk
func (c Config) DebugLogsToDisk() bool {
	return c.FileMaxSizeMB > 0
}
```
