Confirmed: the GraphQL API's `/query` and `/sessions` endpoints (used by unprivileged/authenticated web clients including login and password-change mutations) are wrapped by `loggerFunc`, which logs every request body via `readBody`/`readSanitizedJSON`. This is the strongest available analog to the reported "lack of validation when parsing JSON" bug class within the allowed scope (secret redaction).

### Title
Non-Recursive JSON Body Redaction Leaks Passwords/Secrets in Debug Logs - (File: core/web/router.go)

### Summary
The `loggerFunc` middleware in `core/web/router.go` logs every incoming HTTP/GraphQL request body at debug level via `readBody`, which calls `readSanitizedJSON` to redact sensitive fields before logging [1](#0-0) . However, the redaction logic only inspects **top-level keys** of the parsed JSON object and blindly copies nested objects/arrays into the "cleaned" output without recursing into them [2](#0-1) .

### Finding Description
`readSanitizedJSON` unmarshals the raw request body into `map[string]any` and only redacts a key if `isBlacklisted(k)` matches (password, newpassword, oldpassword, current_password, new_account_password, or any key containing "password") [3](#0-2) . Because the iteration happens only over the top level of the JSON document, any password/secret nested inside a sub-object is copied verbatim (`cleaned[k] = v`) and later re-marshalled into the log line [4](#0-3) .

Chainlink's GraphQL API (`/query`) transports all mutation arguments — including `UpdatePasswordInput` (`oldPassword`/`newPassword`) and `CreateAPITokenInput`/`DeleteAPITokenInput` (`password`) — inside a nested `variables.input` object, e.g. `{"query": "...", "variables": {"input": {"oldPassword": "...", "newPassword": "..."}}}`, as shown in the GraphQL schema and resolver tests [5](#0-4) [6](#0-5) [7](#0-6) . Because `password`/`oldPassword`/`newPassword` are nested under `variables`, the top-level keys the sanitizer actually inspects are only `query` and `variables` — neither of which trips `isBlacklisted`, so the entire `variables` sub-tree (containing the plaintext password) is logged unredacted.

The GraphQL query router itself is registered under the same `loggerFunc` middleware chain applied to all web routes, so any authenticated or unauthenticated request (e.g. failed/successful login attempts through `/sessions`, or `updateUserPassword`/`createAPIToken`/`deleteAPIToken` mutations through `/query`) results in the caller-supplied password being written to the node's debug logs in plaintext.

### Impact Explanation
This is a direct secret-disclosure defect: plaintext user passwords supplied over the network by an authenticated (or, for `/sessions`, unauthenticated) client end up in the operator's log output whenever debug logging is enabled. Log files/aggregators are typically accessible to a wider set of operators/support staff than the credential itself should be, so this creates a path for account takeover if logs are exfiltrated or over-shared, and it's a straightforward violation of secret-redaction expectations already partially implemented by `isBlacklisted`/`blacklist`.

### Likelihood Explanation
Likelihood is limited by two factors: (1) `loggerFunc`'s body logging only fires at `Debugw` level, so it only manifests when debug logging is enabled (common in non-production/troubleshooting scenarios), and (2) the attacker needs read access to the resulting logs, which is typically an operator-only artifact rather than something an unprivileged remote actor can directly read. The trigger itself (sending a JSON body with nested password fields) requires no privilege at all — any client hitting `/query` or `/sessions` can cause their own or another party's password to be logged if debug logging is on.

### Recommendation
Make `readSanitizedJSON` recursive: walk nested maps/slices in the parsed JSON and redact any key matching `isBlacklisted` at every nesting level, not just the top level, before marshalling for the log line. This closes the gap the existing `blacklist` mechanism in `core/web/router.go` was clearly intended to cover.

### Proof of Concept
1. Enable `Debugw`-level logging on a chainlink node.
2. Send a GraphQL mutation to `/query` with a nested `variables.input.oldPassword`/`newPassword` payload matching `UpdatePasswordInput`, e.g.:
```json
{
  "query": "mutation UpdateUserPassword($input: UpdatePasswordInput!) { updateUserPassword(input: $input) { ... } }",
  "variables": {"input": {"oldPassword": "SuperSecret123!", "newPassword": "NewSecret456!"}}
}
```
3. Observe the resulting log line emitted by `loggerFunc` — the `body` field contains the full `variables` object, including `oldPassword`/`newPassword` in plaintext, because `readSanitizedJSON` never inspected keys inside the nested `variables.input` object [8](#0-7) .

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

**File:** core/web/schema/type/user.graphql (L6-9)
```text
input UpdatePasswordInput {
    oldPassword: String!
    newPassword: String!
}
```

**File:** core/web/resolver/user_test.go (L36-42)
```go
	oldPassword := "old"
	variables := map[string]any{
		"input": map[string]any{
			"newPassword": "new",
			"oldPassword": oldPassword,
		},
	}
```

**File:** deployment/environment/web/sdk/internal/schema.graphql (L87-89)
```text
input CreateAPITokenInput {
    password: String!
}
```
