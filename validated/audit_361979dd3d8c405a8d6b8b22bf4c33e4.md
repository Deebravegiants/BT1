Confirmed: `loggerFunc(app.GetLogger())` is registered as a global `engine.Use()` middleware in `NewRouter`, applied before session/auth middleware, so it runs on **every** request to the node's HTTP API — authenticated and unauthenticated alike. [1](#0-0) 

### Title
Incomplete secret-redaction denylist in HTTP request logging exposes sensitive tokens/keys in node logs - (File: core/web/router.go)

### Summary
The Fickling advisory is a textbook CWE-184 (incomplete denylist): a security-relevant blocklist omits an entry (`cProfile`) that is just as dangerous as the entries it does contain, defeating the intended safety guarantee. Chainlink's HTTP request-logging middleware has the same class of defect: its secret-redaction denylist only recognizes "password"-style keys and misses other equally sensitive fields such as `secret`, `accessKey`, `token`, `incomingToken`, `outgoingSecret`, etc.

### Finding Description
Every request to the node's web server passes through `loggerFunc`, which is installed globally via `engine.Use(...)` ahead of authentication/session middleware, so it fires for both authenticated and unauthenticated routes. [1](#0-0) 

`loggerFunc` logs the full request body and query string at Debug level using `readBody`/`redact`, both of which rely on `isBlacklisted` to redact sensitive JSON fields and URL parameters before they are written to logs: [2](#0-1) 

The denylist itself is:
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

This list only catches keys containing the substring "password". It does not cover other secret-bearing field names that flow through the same JSON API bodies handled by this router, e.g.:
- `secret`, `accessKey`, `outgoingToken`, `outgoingSecret` on the External Initiator API (`bridges.ExternalInitiator`, `presenters.ExternalInitiatorAuthentication`). [4](#0-3) [5](#0-4) 
- `incomingToken`, `outgoingToken` on the Bridge Types API (`bridges.BridgeTypeAuthentication`). [6](#0-5) 
- API/user session tokens (`auth.Token{AccessKey, Secret}`) used across the authentication layer. [7](#0-6) 

Just as Fickling's blocklist should have treated `cProfile` the same way it treats `os.system`/`eval`/`exec` (all capable of code execution), this redaction blocklist should treat `secret`/`token`/`accessKey`-style keys the same way it treats `password` (all capable of credential disclosure). The omission is the same root-cause pattern: an allow/deny list intended as a blanket security control that enumerates only a subset of an open-ended, semantically equivalent set of dangerous values.

### Impact Explanation
Because `loggerFunc` runs globally and unconditionally, any JSON body or URL query parameter containing one of the unredacted key names (`secret`, `accessKey`, `token`, `incomingToken`, `outgoingToken`, `outgoingSecret`, etc.) submitted to node HTTP endpoints will be written verbatim into the node's Debug logs. This includes bodies submitted through unauthenticated/lightly-authenticated flows on the same global middleware chain, and any authenticated admin/edit operation (bridge/external-initiator creation, key management, etc.) whose request or response-adjacent field names match these secret-style keys but aren't listed in the request body path. Node operators who ship debug logs to centralized/third-party log aggregation, support bundles, or less-trusted personnel would have those credentials disclosed, enabling request impersonation of bridges/external initiators or reuse of leaked API tokens — a secret/key disclosure vulnerability directly reachable from the same code path unauthenticated clients traverse.

### Likelihood Explanation
The redaction logic is centralized and mechanical (substring/exact match on lower-cased JSON keys), so the gap is deterministic and always triggers whenever a request body includes one of the missing key names — no special conditions required beyond enabling Debug-level logging (a common operational configuration for node operators troubleshooting bridge/EI issues). This mirrors the Fickling bug's "self-contained, no special conditions" characteristic.

### Recommendation
Expand `blacklist` in `core/web/router.go` to include all known secret-bearing field name patterns used across the web API (`secret`, `accesskey`, `token`, `incomingtoken`, `outgoingtoken`, `outgoingsecret`, `apikey`, etc.), and prefer an allowlist-based or substring-match approach (similar to the existing `strings.Contains(lk, "password")` check) generalized to a set of sensitive substrings (`password`, `secret`, `token`, `key`) rather than an exact-match list, so future secret-like fields are redacted by default instead of requiring explicit enumeration.

### Proof of Concept
1. Run a chainlink node with Debug-level logging enabled for the web server.
2. Issue `POST /v2/external_initiators` (or any endpoint whose request/response body traverses the same logging middleware) with a JSON body containing a field named `secret`, `accessKey`, or `outgoingToken`.
3. Observe the node's debug log output produced by `loggerFunc` at `core/web/router.go:556-567` — the value of these fields appears in plaintext instead of `*REDACTED*`, unlike `password`-named fields which are correctly redacted by `isBlacklisted`.

### Citations

**File:** core/web/router.go (L64-72)
```go
	engine.Use(
		otelgin.Middleware("chainlink-web-routes",
			otelgin.WithTracerProvider(otel.GetTracerProvider())),
		limits.RequestSizeLimiter(config.WebServer().HTTPMaxSize()),
		loggerFunc(app.GetLogger()),
		gin.Recovery(),
		cors,
		secureMiddleware(tls.ForceRedirect(), tls.Host(), config.Insecure().DevWebServer()),
	)
```

**File:** core/web/router.go (L588-641)
```go
func readBody(reader io.Reader, lggr logger.Logger) string {
	buf := new(bytes.Buffer)
	_, err := buf.ReadFrom(reader)
	if err != nil {
		lggr.Warn("unable to read from body for sanitization: ", err)
		return "*FAILED TO READ BODY*"
	}

	if buf.Len() == 0 {
		return ""
	}

	s, err := readSanitizedJSON(buf)
	if err != nil {
		lggr.Warn("unable to sanitize json for logging: ", err)
		return "*FAILED TO READ BODY*"
	}
	return s
}

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

**File:** core/bridges/bridge_type.go (L44-53)
```go
// BridgeTypeAuthentication is the record returned in response to a request to create a BridgeType
type BridgeTypeAuthentication struct {
	Name                   BridgeName
	URL                    models.WebURL
	Confirmations          uint32
	IncomingToken          string
	OutgoingToken          string
	MinimumContractPayment *assets.Link
	UseConnectionManager   bool `json:"useConnectionManager"`
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
