This confirms the code as claimed. All citations verified against the actual repository: `readSanitizedJSON` at `core/web/router.go` only iterates top-level keys of the parsed JSON body [1](#0-0) , and the blacklist match at `isBlacklisted` operates on the same flat key set [2](#0-1) . The `loggerFunc` middleware logs the sanitized body at Debug level for every request, including `/query` [3](#0-2) . GraphQL mutations like `UpdateUserPassword` and `CreateAPIToken` accept `Input` structs containing `OldPassword`/`NewPassword`/`Password` fields [4](#0-3) [5](#0-4) , which per GraphQL-over-HTTP convention are submitted nested under `variables.input` in the POST body to `/query` [6](#0-5) , placing the sensitive values two levels deep and outside the reach of the shallow top-level sanitizer. This is a genuine logic bug in the log-redaction code, not a misconfiguration, dependency issue, or something requiring privileged access beyond an authenticated GraphQL user's own password-change/token-creation action — matching the required unprivileged-trigger and concrete-impact criteria.

Audit Report

## Title
Sensitive credentials (passwords) bypass log redaction and are disclosed in plaintext web request debug logs due to shallow top-level-only JSON key matching - (File: core/web/router.go)

## Summary
The Chainlink node's HTTP request logging middleware `loggerFunc` logs the request body for every API call at Debug level, applying a redaction pass (`readSanitizedJSON`) intended to mask sensitive fields like passwords. This redaction only inspects top-level keys of the parsed JSON object, but GraphQL mutations served at `/query` wrap arguments in a nested `variables.input` object, so fields such as `oldPassword`, `newPassword`, and `password` are never redacted and get logged in plaintext at Debug level.

## Finding Description
`loggerFunc` reads and logs the raw request body for every request through the gin router at Debug level via `lggr.Debugw(..., "body", readBody(rdr, lggr), ...)` [7](#0-6) . `readBody` calls `readSanitizedJSON`, which unmarshals the body into a flat `map[string]any` and only redacts keys found at that top level, leaving nested `map[string]any` values (like `variables`) untouched [1](#0-0) . `isBlacklisted` likewise only receives and checks the flat top-level key names [2](#0-1) . This works for REST endpoints with flat bodies (e.g., `UpdatePasswordRequest{OldPassword, NewPassword}` bound directly at top level, and `ChangeAuthTokenRequest{Password}`), but all GraphQL mutations are POSTed to `/query` as `{"query": "...", "variables": {"input": {...}}}` [6](#0-5) . Password-bearing mutations `UpdateUserPassword` (`Input.OldPassword`, `Input.NewPassword`) and `CreateAPIToken` (`Input.Password`) place their sensitive values two levels deep at `variables.input.*` [4](#0-3) [5](#0-4) , so `readSanitizedJSON`'s shallow, non-recursive redaction never reaches or masks them, and the existing blacklist mechanism fails to fulfill its stated purpose for the GraphQL API surface.

## Impact Explanation
When the node operator sets log level to Debug — a documented, supported operational setting used for troubleshooting rather than a misconfiguration exploit — any authenticated GraphQL user's password-change action (`UpdateUserPassword`) or password-gated token creation (`CreateAPIToken`) causes their plaintext old/new password to be written verbatim into the node's log stream. Since node logs are commonly forwarded to centralized log aggregation/monitoring systems, this exposes credential material to a broader set of readers (log-access holders) than intended, constituting a concrete secret-disclosure impact in scope for the Chainlink bounty's key/secret exfiltration category.

## Likelihood Explanation
The trigger requires only Debug-level logging (a supported node configuration) and the acting user performing their own normal password-change or API-token-creation request via the GraphQL API — no additional privilege escalation, host access, or victim interaction is needed. The behavior is deterministic and repeatable: every password-related GraphQL mutation reproduces the leak.

## Recommendation
Make `readSanitizedJSON` recursively walk nested `map[string]any` and slice values (not just the top-level object) so that any key matching the blacklist at any nesting depth is redacted, aligning enforcement with the intent already expressed in `isBlacklisted`.

## Proof of Concept
1. Configure the node with `Log.Level: debug`.
2. As an authenticated user, send:
```
POST /query
{
  "query": "mutation($input: UpdatePasswordInput!) { updateUserPassword(input: $input) { ... } }",
  "variables": { "input": { "oldPassword": "CurrentSecret123!", "newPassword": "NewSecret456!" } }
}
```
3. Inspect the node's Debug log output produced by `loggerFunc`/`readBody`/`readSanitizedJSON` for this request; the logged `body` field contains the full `variables.input` object with `oldPassword` and `newPassword` unredacted, since only the top-level keys `query` and `variables` are checked against the blacklist, not the nested `input.oldPassword`/`input.newPassword` keys.

### Citations

**File:** core/web/router.go (L95-99)
```go
	api.POST("/query",
		auth.AuthenticateGQL(app.AuthenticationProvider(), app.GetLogger().Named("GQLHandler")),
		loader.Middleware(app),
		graphqlHandler(app),
	)
```

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

**File:** core/web/resolver/mutation.go (L934-936)
```go
func (r *Resolver) UpdateUserPassword(ctx context.Context, args struct {
	Input UpdatePasswordInput
}) (*UpdatePasswordPayloadResolver, error) {
```

**File:** core/web/resolver/mutation.go (L990-992)
```go
func (r *Resolver) CreateAPIToken(ctx context.Context, args struct {
	Input struct{ Password string }
}) (*CreateAPITokenPayloadResolver, error) {
```
