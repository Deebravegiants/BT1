### Title
Sensitive credentials leak into node debug logs because request-body redaction only blacklists password fields - ([File: core/web/router.go])

### Summary
The 8ight Finance loss stemmed from operators' private keys/secrets being exposed in plaintext outside of any protected secure storage. The nearest unprivileged-actor analog in this codebase is not a private-key leak, but a structurally identical class of bug: the chainlink node's internet-facing HTTP logging middleware writes the raw client request body to logs, and the redaction logic that is supposed to scrub sensitive fields only recognizes password-shaped field names — not the `secret`, `accessKey`, or `token` fields used throughout the External Initiator and API-token authentication flows.

### Finding Description
Every request that flows through the node's gin router (excluding excluded paths) is wrapped by `loggerFunc`, which reads the entire request body and logs it via `lggr.Debugw(...)` together with the redacted query string: [1](#0-0) 

The body is passed through `readBody` → `readSanitizedJSON`, which redacts only keys present in a hardcoded `blacklist`: [2](#0-1) 

That blacklist contains exclusively password-style keys (`password`, `newpassword`, `oldpassword`, `current_password`, `new_account_password`) and a substring check for `"password"`. It does not redact `secret`, `accessKey`, `token`, `incomingSecret`, `outgoingSecret`, `outgoingToken`, `clientSecret`, or similar credential field names that are integral to the node's own authentication primitives, e.g.:

- `auth.Token{AccessKey, Secret}` used for API tokens and External Initiator auth [3](#0-2) 
- `ExternalInitiator{AccessKey, HashedSecret, OutgoingSecret, OutgoingToken}` [4](#0-3) 
- The `X-Chainlink-EA-AccessKey` / `X-Chainlink-EA-Secret` headers used to authenticate External Initiator requests [5](#0-4) 

Because `loggerFunc` logs the request body of every route (this middleware sits ahead of route-specific handling in the router setup), any endpoint that accepts a JSON field literally named `secret`, `token`, `accessKey`, etc., in its request body will have that value written into the node's debug logs unredacted, alongside the request path and client IP. The only field class that is protected is passwords.

### Impact Explanation
If a node operator runs with debug logging enabled (a supported and documented configuration, not a misconfiguration), any credential-bearing field submitted in a request body that isn't literally called "password" is persisted to node logs in plaintext. Log files/aggregation pipelines are frequently exported to third parties (SIEM, cloud logging, support bundles), broadening exposure well beyond the node operator, mirroring the "plaintext secret exposed outside of a secure boundary" root cause of the 8ight Finance incident (albeit here the root cause is a missed redaction rule, not human error posting to Facebook/Google Docs). This is a **secret disclosure via logs** issue reachable from ordinary node-API usage, not a network/operator-only or dependency bug.

### Likelihood Explanation
The External Initiator subsystem authenticates over headers (not logged by this middleware), which limits practical exposure via this exact path today. However, the underlying control is a low-effort, config-driven allowlist maintained by string literal, and it is trivially inconsistent with the credential vocabulary used elsewhere in the very same package (`auth.Token.Secret`, `ExternalInitiator.OutgoingSecret`, etc.). Any future or existing body-based endpoint that reuses these field names (or camelCase variants like `incomingSecret`/`outgoingToken` seen in `ExternalInitiatorAuthentication`) will silently leak credentials into logs whenever `Debugw` is enabled, without any additional attacker action beyond making a normal, valid API request. This is a design/maintenance gap rather than a directly exploitable remote bypass, so likelihood is assessed as **Medium**.

### Recommendation
Expand `isBlacklisted` in `core/web/router.go` to redact by substring match on a broader set of credential terms — `secret`, `token`, `accesskey`, `apikey`, `clientsecret`, `privatekey` — in addition to `password`, and consider switching from a denylist to an allowlist model or a marker-based approach (e.g., tagging sensitive struct fields) so newly introduced credential fields are redacted by default rather than requiring every field name to be manually added to `blacklist`.

### Proof of Concept
1. Enable debug-level logging on a chainlink node (`Log.Level = 'debug'`).
2. Issue any authenticated request whose JSON body contains a field literally named `secret`, `token`, or `accessKey` (any endpoint that in the future accepts such fields, or via a custom/extended bridge/EI management flow that echoes tokens in the body rather than headers).
3. Inspect node logs; observe that the `body` field in the `loggerFunc` log line contains the credential value unredacted, because `isBlacklisted` only matches password-shaped keys: [6](#0-5)

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

**File:** core/auth/auth.go (L21-25)
```go
// Token is used for API authentication.
type Token struct {
	AccessKey string `json:"accessKey"`
	Secret    string `json:"secret"`
}
```

**File:** core/bridges/external_initiator.go (L21-34)
```go
// ExternalInitiator represents a user that can initiate runs remotely
type ExternalInitiator struct {
	ID             int64
	Name           string
	URL            *models.WebURL
	AccessKey      string
	Salt           string
	HashedSecret   string
	OutgoingSecret string
	OutgoingToken  string

	CreatedAt time.Time
	UpdatedAt time.Time
}
```

**File:** core/web/auth/auth.go (L119-124)
```go
func AuthenticateExternalInitiator(c *gin.Context, store Authenticator) error {
	ctx := c.Request.Context()
	eia := &auth.Token{
		AccessKey: c.GetHeader(static.ExternalInitiatorAccessKeyHeader),
		Secret:    c.GetHeader(static.ExternalInitiatorSecretHeader),
	}
```
