### Title
Sensitive fields inside GraphQL `variables` (e.g. passwords) are not redacted before being written to application logs at Debug level - (File: core/web/router.go)

### Summary
Chainlink's HTTP request logging middleware sanitizes JSON request bodies before logging them, but the sanitization only inspects **top-level** JSON keys against a password-related blacklist. GraphQL requests (used by the Operator UI/admin API, served at `/query`) wrap all mutation arguments inside a nested `variables` object, so fields such as `oldPassword`/`newPassword` (for `UpdateUserPassword`) or `password` (for `CreateAPIToken`) are never matched by the blacklist and are logged in plaintext. This mirrors the CVE-2019-10217 bug class: a mechanism intended to suppress logging of sensitive fields (`no_log`) exists but is not applied to all the fields that actually carry sensitive data, so secrets leak into logs.

### Finding Description
`loggerFunc` wraps every HTTP request (including the GraphQL endpoint) and logs the sanitized request body at Debug level: [1](#0-0) 

The sanitization function `readSanitizedJSON` only redacts a key if it appears as a **top-level** key of the parsed JSON object and matches `isBlacklisted`: [2](#0-1) 

```go
cleaned := map[string]any{}
for k, v := range dst {
    if isBlacklisted(k) {
        cleaned[k] = "*REDACTED*"
        continue
    }
    cleaned[k] = v
}
```

`isBlacklisted` matches only literal password-ish key names: [3](#0-2) 

A GraphQL POST body has the shape `{"query": "...", "variables": {...}, "operationName": "..."}`. The top-level keys are `query`, `variables`, `operationName` — none of which are blacklisted — so the entire `variables` map (including any nested password fields) is copied through unredacted and marshaled into the logged JSON string.

Concretely, `UpdateUserPassword`'s GraphQL input carries `oldPassword`/`newPassword` as nested `variables` fields: [4](#0-3) 

and `CreateAPIToken`'s input carries a plaintext `password`: [5](#0-4) 

Because the request-body sanitizer never recurses into nested objects, these values are written verbatim into the Debug-level request log by `loggerFunc`, which is enabled by default at debug verbosity and is the same code path used for every authenticated admin/API request.

### Impact Explanation
This causes disclosure of a user's plaintext current/new password (or other credentials submitted through GraphQL mutations) into the node's own log files/streams whenever Debug logging is enabled. Log files are commonly aggregated, shipped to centralized logging systems, or accessible to operators/support staff who should not otherwise learn a user's password. This is a genuine secret-redaction gap analogous to the ansible `no_log` bug: a redaction/no-log mechanism exists, but is incomplete for the actual sensitive fields that flow through the request path.

### Likelihood Explanation
Any authenticated UI/API user who calls `UpdateUserPassword`, `CreateAPIToken`, or any other GraphQL mutation carrying secret-bearing arguments will trigger this on every request, as long as the node's log level is Debug (a supported, commonly used operational configuration — `core/services/chainlink/config_general_state.go` shows `LogLevel`/`LogSQL` are configurable at runtime via the admin API). No attacker-controlled bypass or privilege escalation is needed to trigger the leak — it happens as a side effect of normal, legitimate password-management operations.

### Recommendation
Extend `readSanitizedJSON` (and `isBlacklisted`) to recursively walk nested JSON objects/arrays (in particular the GraphQL `variables` object) and redact any blacklisted key at any depth, not just the top level. Consider also blacklisting additional sensitive key names beyond `*password*` (e.g. `token`, `secret`, `clientSecret`) consistent with the fields already treated as secrets elsewhere in the codebase (e.g. `core/store/models/secrets.go`, `core/config/toml/types.go` `WebServerOIDCSecrets.ClientSecret`).

### Proof of Concept
1. Start the node with `Log.Level = "debug"`.
2. As an authenticated user, send a GraphQL request to `/query`:
```json
POST /query
{
  "query": "mutation($input: UpdatePasswordInput!) { updatePassword(input: $input) { ... } }",
  "variables": { "input": { "oldPassword": "CurrentSecretPass1", "newPassword": "NewSecretPass2" } }
}
```
3. Observe the node's Debug log output produced by `loggerFunc` — the log line for this request contains the `body` field with the full JSON, including `oldPassword` and `newPassword` in plaintext, because `readSanitizedJSON` only checked the top-level keys `query`/`variables`/`operationName`, none of which are blacklisted.

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

**File:** core/web/resolver/mutation.go (L934-951)
```go
func (r *Resolver) UpdateUserPassword(ctx context.Context, args struct {
	Input UpdatePasswordInput
}) (*UpdatePasswordPayloadResolver, error) {
	if err := authenticateUser(ctx); err != nil {
		return nil, err
	}

	session, ok := webauth.GetGQLAuthenticatedSession(ctx)
	if !ok {
		return nil, errors.New("couldn't retrieve user session")
	}

	dbUser, err := r.App.AuthenticationProvider().FindUser(ctx, session.User.Email)
	if err != nil {
		return nil, err
	}

	if !utils.CheckPasswordHash(args.Input.OldPassword, string(dbUser.HashedPassword)) {
```

**File:** core/web/resolver/mutation.go (L990-1013)
```go
func (r *Resolver) CreateAPIToken(ctx context.Context, args struct {
	Input struct{ Password string }
}) (*CreateAPITokenPayloadResolver, error) {
	if err := authenticateUser(ctx); err != nil {
		return nil, err
	}

	session, ok := webauth.GetGQLAuthenticatedSession(ctx)
	if !ok {
		return nil, errors.New("Failed to obtain current user from context")
	}
	dbUser, err := r.App.AuthenticationProvider().FindUser(ctx, session.User.Email)
	if err != nil {
		return nil, err
	}

	err = r.App.AuthenticationProvider().TestPassword(ctx, dbUser.Email, args.Input.Password)
	if err != nil {
		r.App.GetAuditLogger().Audit(audit.APITokenCreateAttemptPasswordMismatch, map[string]any{"user": dbUser.Email})

		return NewCreateAPITokenPayload(nil, map[string]string{
			"password": "incorrect password",
		}), nil
	}
```
