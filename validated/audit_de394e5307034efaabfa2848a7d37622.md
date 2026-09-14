### Title
Unprivileged-triggered plaintext credential logging via shallow JSON redaction in gin request logger - (File: `core/web/router.go`)

### Summary
The chainlink node's HTTP request-logging middleware (`loggerFunc`) logs the full request body for every API request at debug level, applying only a shallow, top-level-key redaction (`readSanitizedJSON`/`isBlacklisted`) before logging. Because many chainlink API payloads (login, session, API-token, external-initiator endpoints) wrap sensitive fields inside nested JSON structures (e.g., JSONAPI `data.attributes.*`), a top-level-only blacklist check will not redact nested `password`/`secret` fields, causing credentials submitted by any unauthenticated/unprivileged client to be written to node logs in plaintext — the same bug class as the Argo Workflows advisory (CWE-522: logging structured request/credential data without adequate field-level redaction, exposing secrets to anyone with pod/log read access).

### Finding Description
`loggerFunc` reads the raw request body before running the handler chain and logs it after the request completes: [1](#0-0) 

The sanitization helper only redacts keys that are blacklisted at the **top level** of the JSON body: [2](#0-1) 

`redact` for the query string performs the identical top-level-only substitution: [3](#0-2) 

This middleware runs on `/v2/...` API routes globally (via `Router(...)`), meaning it fires for authentication endpoints too — e.g. session creation (login with password), `CreateAPIToken` GraphQL mutation (which accepts a `password` field), and the external initiator creation endpoint whose response is `ExternalInitiatorAuthentication` containing `AccessKey`/`Secret`/`OutgoingToken`/`OutgoingSecret`: [4](#0-3) [5](#0-4) 

Because chainlink's JSON:API-style request/response bodies typically nest attributes under a `data` object (as seen in the JSONAPI resource types used across `core/web/presenters`), a flat blacklist check against top-level keys such as `password` or `secret` would not match a nested `data.attributes.password` field. This means these credential values would be logged verbatim in the debug-level `"body"` field emitted by `loggerFunc`, in the same way the Argo executor logged the entire `ArtifactDriver` struct (including nested credential fields) to a structured logger without deep field-level scrubbing.

I was **not able to retrieve the definition of `isBlacklisted(k)`** within available iterations, so I cannot confirm the exact list of blacklisted keys or whether it recurses into nested objects. This is a material uncertainty: if `isBlacklisted`/`readSanitizedJSON` in fact walks nested structures or the blacklist includes wrapper keys like `data`, the redaction would be effective and this finding would not hold. This should be verified directly in the codebase (`core/web/router.go`, near the `redact`/`isBlacklisted` definitions) before treating this as confirmed.

### Impact Explanation
If nested credential fields are not redacted, any client submitting a login, API-token-creation, session, or external-initiator request causes the node to write that request's/response's plaintext secret material (session password, generated API access key/secret, external initiator `OutgoingSecret`/`OutgoingToken`) into its own logs at debug level. Anyone with read access to the node's logs (log aggregation systems, ops staff, or misconfigured log-shipping/monitoring integrations) could recover credentials that were never meant to be persisted outside the database in hashed form. This mirrors the Argo advisory's impact: credential material intended to stay secret is captured verbatim in a log sink reachable by parties who should not have access to raw secrets.

### Likelihood Explanation
Likelihood is *conditional and unverified*: it depends entirely on (a) whether debug-level logging is enabled in the deployment (it is opt-in via log level configuration) and (b) whether `isBlacklisted`/`readSanitizedJSON` truly fails to redact nested fields, which I could not confirm due to the missing function body. If both conditions hold, the trigger requires no privilege at all — an external, unauthenticated caller hitting `/v2/sessions`, `/v2/external_initiators`, or the `createAPIToken` GraphQL mutation is sufficient to cause the log write, since `loggerFunc` always executes and always attempts to log the body regardless of authentication outcome.

### Recommendation
- Confirm the actual body/definition of `isBlacklisted` and `readSanitizedJSON` and verify whether redaction recurses into nested JSON objects (especially JSONAPI `data.attributes.*` payloads).
- If redaction is shallow, make `readSanitizedJSON` recursively walk all nested maps/arrays and redact any key matching the sensitive-field blacklist at any depth, not just the top level.
- Extend the same nested-aware redaction to response bodies if/when those are ever logged, and audit all `Debugw`/`Infow` call sites elsewhere in `core/web` for similar struct-dumping patterns.
- Consider excluding known-sensitive endpoints (sessions, external initiators, API token creation) from full-body debug logging entirely, logging only non-sensitive metadata for those routes.

### Proof of Concept
Not independently verified due to inability to confirm `isBlacklisted`'s contents in the available iterations. A concrete PoC would be: enable debug logging, `POST /v2/external_initiators` with a JSON body wrapping the request in a `data.attributes` envelope (if the controller accepts that shape) or trigger `createAPIToken`, then inspect node logs for the `"body"` field of the corresponding `loggerFunc` debug entry to check whether `secret`/`password`/`accessKey` values appear unredacted. This step must be completed against the real `core/web/router.go` `isBlacklisted` implementation to determine whether this is exploitable as described.

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

**File:** core/web/router.go (L631-640)
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

**File:** deployment/environment/web/sdk/internal/schema.graphql (L87-93)
```text
input CreateAPITokenInput {
    password: String!
}

type CreateAPITokenSuccess {
    token: APIToken!
}
```
