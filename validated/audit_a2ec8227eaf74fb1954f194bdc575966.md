## Finding

### Title
FreeIPA-style plaintext password logging analog: GraphQL/nested-JSON password fields bypass HTTP request-body redaction - ([File: core/web/router.go])

### Summary
The Chainlink node's HTTP debug-request logger redacts sensitive fields (e.g. `password`) only at the top level of a JSON request body. Any endpoint whose request schema nests a password-bearing field one level deeper — most notably the GraphQL endpoint, whose mutations (e.g. password change/reset, API-token creation) place arguments under a `variables` object — will have the plaintext password written to the node's debug logs, mirroring the FreeIPA batch-logging flaw where nested/batched command arguments containing passwords bypassed audit sanitization.

### Finding Description
The request logging middleware `loggerFunc` in [1](#0-0)  buffers and logs every request body at `Debug` level, including the sanitized JSON body produced by `readBody`/`readSanitizedJSON`.

`readSanitizedJSON` only unmarshals the body into a flat `map[string]any` and iterates the **top-level keys**, replacing values with `*REDACTED*` only when the top-level key itself matches `isBlacklisted` (i.e. contains "password"): [2](#0-1) [3](#0-2) 

Because the redaction walk never recurses into nested objects/arrays, any request whose password field is embedded one or more levels deep in the JSON payload is logged verbatim. This is structurally identical to the FreeIPA advisory's root cause: a generic logging/serialization path that inspects only the outer structure of a request/command envelope and misses embedded secret arguments nested inside batched or wrapped payloads.

Chainlink's GraphQL API (mounted under the same router and subject to `loggerFunc`) is the concrete reachable case: GraphQL requests are POSTed as `{"query": "...", "variables": {...}}`. Sensitive arguments such as passwords for mutations resolved in [4](#0-3)  (e.g., `updatePassword`, `createAPIToken`/`setSQLLogging`-style password-gated mutations) are supplied inside the nested `variables` object, not as a top-level JSON key. `isBlacklisted` never inspects `variables.password`, so `cleaned["variables"]` retains the full nested map (including the raw password string) and is marshaled and logged as-is when `Log.Level = 'debug'`.

Separately, `UserController.UpdatePassword`/`NewAPIToken`/`DeleteAPIToken` in [5](#0-4)  and `ChangeAuthTokenRequest`/`SessionRequest` in [6](#0-5)  do use top-level `password`/`oldPassword`/`newPassword` keys, which the current blacklist does correctly catch (`isBlacklisted` matches on substring "password" case-insensitively) — so the REST-only paths are not the exposure. The exposure is specifically routes/protocols (GraphQL, or any future/JSON-batch-style endpoint) that wrap credentials inside a nested container object.

### Impact Explanation
When `Log.Level` is `debug` (a supported, documented, non-default but commonly used-for-troubleshooting configuration, as shown in [7](#0-6) ), any unprivileged or low-privileged client performing a password-related GraphQL mutation will have their plaintext password written to the node's log files/stdout. Anyone with read access to node logs (log aggregation systems, support/ops staff, or an attacker who compromises log storage) can recover user passwords, enabling account takeover of the FreeIPA/Chainlink-node operator API. This matches CWE-200 (information exposure) at the same severity class as the original advisory.

### Likelihood Explanation
Likelihood is moderate: it requires `Log.Level=debug` (or more verbose) to be enabled, which is a legitimate and reasonably common operational setting for troubleshooting, and requires the requester to submit a GraphQL mutation containing a password argument — a normal, expected, unprivileged user action (e.g., self password change), not a specially crafted attack payload. No authentication bypass is needed to trigger the leak; only a log-level configuration choice is required for the leak to materialize.

### Recommendation
Make the request-body sanitizer in `readSanitizedJSON` recursive: walk nested objects and arrays (not just the top-level map) and redact any key matching the blacklist regardless of nesting depth. Additionally, for the GraphQL endpoint specifically, add explicit sanitization of the `variables` sub-object (and consider blacklisting the entire GraphQL body by default, redacting known sensitive argument names such as `password`, `oldPassword`, `newPassword`) before it reaches `loggerFunc`.

### Proof of Concept
1. Set `Log.Level = 'debug'` in the node config.
2. Send a GraphQL mutation to `/query` that changes the current user's password, e.g.:
```json
{"query":"mutation($input: UpdatePasswordInput!){ updatePassword(input: $input){ ... } }","variables":{"input":{"oldPassword":"CorrectHorseBattery1","newPassword":"NewSecretPass1!"}}}
```
3. Inspect the node's debug logs produced by `loggerFunc` — the `body` field will contain the full `variables` object with `oldPassword`/`newPassword` in plaintext, because `readSanitizedJSON` only checked the top-level keys `query` and `variables`, not the nested `oldPassword`/`newPassword` keys inside `variables.input`.

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

**File:** core/web/resolver/user.go (L1-18)
```go
package resolver

import (
	"github.com/graph-gophers/graphql-go"

	"github.com/smartcontractkit/chainlink/v2/core/sessions"
)

type clearSessionsError struct{}

func (e clearSessionsError) Error() string {
	return "failed to clear non current user sessions"
}

type failedPasswordUpdateError struct{}

func (e failedPasswordUpdateError) Error() string {
	return "failed to update current user password"
```

**File:** core/web/user_controller.go (L26-31)
```go
// UpdatePasswordRequest defines the request to set a new password for the
// current session's User.
type UpdatePasswordRequest struct {
	OldPassword string `json:"oldPassword"`
	NewPassword string `json:"newPassword"`
}
```

**File:** core/sessions/session.go (L16-44)
```go
type SessionRequest struct {
	Email          string `json:"email"`
	Password       string `json:"password"`
	WebAuthnData   string `json:"webauthndata"`
	WebAuthnConfig WebAuthnConfiguration
	SessionStore   *WebAuthnSessionStore
}

// Session holds the unique id for the authenticated session.
type Session struct {
	ID        string    `json:"id"`
	Email     string    `json:"email"`
	LastUsed  time.Time `json:"lastUsed"`
	CreatedAt time.Time `json:"createdAt"`
}

// NewSession returns a session instance with ID set to a random ID and
// LastUsed to now.
func NewSession() Session {
	return Session{
		ID:       utils.NewBytes32ID(),
		LastUsed: time.Now(),
	}
}

// Changeauth.TokenRequest is sent when updating a User's authentication token.
type ChangeAuthTokenRequest struct {
	Password string `json:"password"`
}
```

**File:** testdata/scripts/node/validate/disk-based-logging.txtar (L9-11)
```text
-- config.toml --
Log.Level = 'debug'

```
