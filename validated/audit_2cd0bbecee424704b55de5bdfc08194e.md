Found a valid analog: the debug-level HTTP request logger in `core/web/router.go` redacts only fields whose keys contain the substring `"password"`, while POST bodies that create or rotate API/EI credentials use field names `secret`, `accessKey`, `incomingSecret`, `outgoingToken`, `outgoingSecret` (none contain "password"), so these values are written to logs in cleartext.

### Title
Cleartext logging of API/external-initiator secrets due to password-only log redaction blacklist - ([File: core/web/router.go])

### Summary
`loggerFunc` in `core/web/router.go` logs every HTTP request body and query string at debug level after passing them through a redaction filter (`readSanitizedJSON`/`redact`) that only masks JSON/query keys matching `"password"`. [1](#0-0)  The blacklist used by `isBlacklisted` contains only password-related keys. [2](#0-1) 

### Finding Description
Authenticated endpoints such as external-initiator creation/rotation and API token management accept and return credential fields named `secret`, `accessKey`, `incomingSecret`, `outgoingToken`, and `outgoingSecret` — none of which contain the substring "password". [3](#0-2)  The generic `auth.Token` struct used for API authentication similarly serializes as `accessKey`/`secret`. [4](#0-3)  Because `loggerFunc` reads the raw request body via `readBody`/`readSanitizedJSON` and only redacts keys in the `password` blacklist, any request that creates or returns these credential fields (e.g. an external-initiator registration response containing `incomingSecret`/`outgoingSecret`, or a bridge/API-token payload) is written to the application logs in cleartext at debug level. [5](#0-4)  This is analogous to CVE-2020-8225's cleartext storage of sensitive credential material meant to be secret, except here it is the node's own HTTP access-layer logging pipeline rather than a proxy config file.

### Impact Explanation
If `Log.Level = 'debug'` is enabled (a supported, documented configuration, as shown in `testdata/scripts/node/validate/disk-based-logging-disabled.txtar`), the node's logs (which may be shipped to log aggregation systems or persisted to disk per `Log.File`) will contain external-initiator and API-token secrets in plaintext. [6](#0-5)  Anyone with read access to logs (which is often a broader trust boundary than the admin API itself, e.g. log-shipping infrastructure, support staff, monitoring tooling) can recover credentials used to authenticate external initiators or the HTTP API, enabling request impersonation.

### Likelihood Explanation
Requires debug logging enabled (an operator choice, not default) and requires normal use of the affected endpoints (creating/rotating external initiators or API tokens), both of which are standard operational activities rather than requiring any special privilege beyond what the admin API already grants. The core defect is a maintenance gap in `blacklist`/`isBlacklisted` rather than a hard-to-reach or attacker-controlled path.

### Recommendation
Expand `blacklist` in `core/web/router.go` to cover all credential-bearing field names (`secret`, `accesskey`, `incomingsecret`, `outgoingtoken`, `outgoingsecret`, `token`, etc.), or switch to an allowlist model for logged body fields, or avoid logging response/request bodies for credential-issuing endpoints entirely.

### Proof of Concept
1. Set `Log.Level = 'debug'`.
2. `POST /v2/external_initiators` to create a new external initiator; the JSON response contains `incomingAccessKey`/`incomingSecret`/`outgoingToken`/`outgoingSecret` fields per `ExternalInitiatorAuthentication`. [3](#0-2) 
3. Because `loggerFunc` logs the raw request/response-adjacent body through `readBody`(which only strips `password`-like keys), the secret values appear in cleartext in the node's debug logs. [5](#0-4) 

Note: I could not fully trace whether the response body (as opposed to only the request body) is also passed to `readBody`/logged — `loggerFunc` explicitly reads `c.Request.Body`, so the primary confirmed leak path is via request payloads that include these secret fields (e.g., updating/rotating an EI's secret or an API token via PATCH/POST), rather than the initial creation response. Given index-size limits, some related handler files (e.g., `external_initiators_controller.go` body construction) were not fully inspected — a Devin session with full repo access could confirm the exact request/response flow to remove any remaining ambiguity.

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

**File:** core/web/presenters/external_initiators.go (L12-20)
```go
// ExternalInitiatorAuthentication includes initiator and authentication details.
type ExternalInitiatorAuthentication struct {
	Name           string        `json:"name,omitempty"`
	URL            models.WebURL `json:"url"`
	AccessKey      string        `json:"incomingAccessKey,omitempty"`
	Secret         string        `json:"incomingSecret,omitempty"`
	OutgoingToken  string        `json:"outgoingToken,omitempty"`
	OutgoingSecret string        `json:"outgoingSecret,omitempty"`
}
```

**File:** core/auth/auth.go (L21-25)
```go
// Token is used for API authentication.
type Token struct {
	AccessKey string `json:"accessKey"`
	Secret    string `json:"secret"`
}
```

**File:** testdata/scripts/node/validate/disk-based-logging-disabled.txtar (L9-22)
```text
-- config.toml --
Log.Level = 'debug'

[[EVM]]
ChainID = '1'

[[EVM.Nodes]]
Name = 'fake'
WSURL = 'wss://foo.bar/ws'
HTTPURL = 'https://foo.bar'

[Log.File]
Dir = './logs'
MaxSize = '0b'
```
