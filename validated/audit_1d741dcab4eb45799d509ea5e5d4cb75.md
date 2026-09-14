## Finding

Local (disk) logging of sensitive GraphQL request bodies (e.g., plaintext user passwords) is not properly redacted because the sanitization logic only inspects **top-level** JSON keys of the raw HTTP body, while the GraphQL protocol nests all mutation arguments inside a `variables` object.

### Root cause

`core/web/router.go`'s `loggerFunc` middleware is registered globally via `engine.Use(...)` [1](#0-0)  and unconditionally logs the full request body at `Debug` level for every route, including the GraphQL endpoint `POST /query` which is wired through `graphqlHandler(app)` [2](#0-1) :

```go
lggr.Debugw(fmt.Sprintf("%s %s", c.Request.Method, c.Request.URL.Path),
    ...
    "body", readBody(rdr, lggr),
    ...
)
``` [3](#0-2) 

`readBody` delegates to `readSanitizedJSON`, which only unmarshals the body into a flat `map[string]any` and redacts matching **top-level** keys:

```go
func readSanitizedJSON(buf *bytes.Buffer) (string, error) {
	var dst map[string]any
	...
	cleaned := map[string]any{}
	for k, v := range dst {
		if isBlacklisted(k) {
			cleaned[k] = "*REDACTED*"
			continue
		}
		cleaned[k] = v
	}
	...
}
``` [4](#0-3) 

There is no recursion into nested objects. Since the GraphQL wire format sends bodies shaped like `{"query": "...", "variables": {"input": {"oldPassword": "...", "newPassword": "..."}}, "operationName": "..."}`, the top-level keys are `query`, `variables`, and `operationName` — never `password`/`oldpassword`/`newpassword` — so `isBlacklisted` never matches and the plaintext credentials inside `variables.input` are written unredacted into the local log stream.

This is directly exploitable via the `UpdateUserPassword` mutation, which any authenticated (non-admin) user can invoke on their own account:

```go
func (r *Resolver) UpdateUserPassword(ctx context.Context, args struct {
	Input UpdatePasswordInput
}) (*UpdatePasswordPayloadResolver, error) {
	if err := authenticateUser(ctx); err != nil {
		return nil, err
	}
	...
``` [5](#0-4) 

The GraphQL variables for this mutation are `{"input": {"oldPassword": "<plaintext>", "newPassword": "<plaintext>"}}`, which is nested one level deeper than the redaction logic checks. The same gap applies to `CreateAPIToken`/`DeleteAPIToken` (`{"input": {"password": "..."}}`) [6](#0-5) .

### Impact

When `Log.Level = 'debug'` is enabled (a supported, documented configuration, not an exotic edge case — see the node-validate test fixtures that explicitly exercise `Log.Level = 'debug'` with `Log.File` disk logging) [7](#0-6) , any authenticated user's plaintext old/new password (or API-token password) submitted through the standard GraphQL UI/API is persisted verbatim into the node's local log files, bypassing the exact redaction mechanism (`blacklist`/`isBlacklisted`) that was purpose-built to prevent this [8](#0-7) . This mirrors CVE-2019-20852's bug class (local logging not blocking sensitive data) — the redaction exists but has a structural blind spot for nested JSON, so an unprivileged authenticated user's own credential-change request causes credential disclosure into node-local logs. This differs from a self-inflicted no-impact scenario because it broadens the operational exposure of that credential (log aggregation pipelines, backups, support/log-sharing, other admins with log access, etc.) beyond the user who set it, and the same shallow filter would also fail to redact other multi-level sensitive fields (e.g., bridge/EI secrets or tokens supplied via nested GraphQL inputs) if similarly named at a nested level not literally `password`.

### Recommendation
Make `readSanitizedJSON` recursive (walk all nested maps/arrays and redact any blacklisted key at any depth), and/or specifically strip `variables` payloads for known-sensitive GraphQL mutations before Debug logging, rather than relying on a flat top-level key scan.

### Proof of Concept
1. Set `Log.Level = 'debug'` and enable `Log.File` in the node config.
2. As any authenticated (non-admin) user, send a GraphQL request to `POST /query`:
```json
{"query":"mutation($input: UpdatePasswordInput!){ updatePassword(input:$input){ user{ id } } }",
 "variables":{"input":{"oldPassword":"MyRealOldPass123","newPassword":"MyRealNewPass456"}}}
```
3. Inspect the node's local log file — the Debug-level `body` field for `POST /query` contains the full unredacted `variables.input.oldPassword`/`newPassword` values, because `isBlacklisted` never sees the top-level keys `oldPassword`/`newPassword` (only `query`, `variables`, `operationName` are checked).

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

**File:** core/web/router.go (L95-99)
```go
	api.POST("/query",
		auth.AuthenticateGQL(app.AuthenticationProvider(), app.GetLogger().Named("GQLHandler")),
		loader.Middleware(app),
		graphqlHandler(app),
	)
```

**File:** core/web/router.go (L556-562)
```go
		lggr.Debugw(fmt.Sprintf("%s %s", c.Request.Method, c.Request.URL.Path),
			"method", c.Request.Method,
			"status", c.Writer.Status(),
			"path", c.Request.URL.Path,
			"ginPath", c.FullPath(),
			"query", redact(c.Request.URL.Query()),
			"body", readBody(rdr, lggr),
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

**File:** core/web/resolver/mutation.go (L934-957)
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
		r.App.GetAuditLogger().Audit(audit.PasswordResetAttemptFailedMismatch, map[string]any{"user": dbUser.Email})

		return NewUpdatePasswordPayload(nil, map[string]string{
			"oldPassword": "old password does not match",
		}), nil
	}
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

**File:** testdata/scripts/node/validate/disk-based-logging.txtar (L9-22)
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
MaxSize = '1.00mb'
Dir = './logs'
```
