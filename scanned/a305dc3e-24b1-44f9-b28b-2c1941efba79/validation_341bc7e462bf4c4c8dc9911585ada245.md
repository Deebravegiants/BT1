### Title
Login endpoint discloses distinct error messages for non-existent vs. existing usernames, enabling user enumeration - (File: core/sessions/localauth/orm.go)

### Summary
The unauthenticated `POST /sessions` login endpoint returns different, message-distinguishable errors depending on whether the submitted email corresponds to an existing user or not, allowing an unprivileged attacker to enumerate valid Chainlink node UI/API usernames — directly analogous to CVE-2019-18986 (Pimcore), where distinct "forgot password" responses for valid vs. invalid users enabled username brute-forcing.

### Finding Description
`SessionsController.Create` handles the login POST body and forwards it to `AuthenticationProvider().CreateSession`, and on any failure passes the raw `error` straight into `jsonAPIError`, which serializes `err.Error()` into the JSON response body unless the error is already a `*models.JSONAPIErrors`: [1](#0-0) [2](#0-1) 

In the local-auth provider (the default `AuthenticationProvider`), `CreateSession` first calls `FindUser`, and if the user is not found, the raw datastore error (e.g., a `sql.ErrNoRows`-derived error) is returned unmodified. If the user *is* found but the password is wrong, a distinct, hard-coded `"Invalid password"` error is returned instead: [3](#0-2) 

Because these two error paths produce different text in the JSON response body (`err.Error()` from the DB "no rows" case vs. the literal string `"Invalid password"`), an unauthenticated caller can distinguish "email does not exist" from "email exists, wrong password" purely by comparing response bodies for the exact same HTTP status code (`401 Unauthorized`) returned by the controller: [1](#0-0) 

This is the same bug class as the Pimcore advisory: distinct application responses for "user doesn't exist" vs. "user exists, credential mismatch" on an authentication-adjacent endpoint, enabling brute-force enumeration of valid account identifiers (in this case Chainlink node operator email/usernames).

### Impact Explanation
Successful enumeration of valid usernames on a Chainlink node's operator UI/API materially lowers the bar for subsequent credential-stuffing or brute-force password attacks against the node's admin/operator accounts, which control job creation, key management, and fund-moving transactions. While this alone is not full account takeover, it is a legitimate CWE-307-class weakness (Improper Restriction of Excessive Authentication Attempts / information disclosure aiding brute force), matching the severity class of the disclosed CVE (username disclosure via distinct auth responses).

### Likelihood Explanation
The `/sessions` endpoint is unauthenticated by design (it's the login endpoint) and reachable directly by any network client that can reach the node's web UI/API port. No privileged access or special conditions are required — an attacker simply submits login attempts with different email addresses and inspects the returned error text, which is a low-effort, highly likely-to-be-exploited condition once the port is reachable.

### Recommendation
Normalize the error returned from `CreateSession` in `core/sessions/localauth/orm.go` (and equivalent OIDC/LDAP `localLoginFallback` paths, which have the same `FindUser`-then-distinct-error pattern) so that "user not found" and "invalid password" produce an identical generic error (e.g., `"invalid email or password"`) with identical HTTP status and identical response body shape, and ensure `jsonAPIError` does not leak provider-specific/database error text (`err.Error()`) for authentication failures.

### Proof of Concept
1. `POST /sessions` with `{"email":"realuser@example.com","password":"wrongpass"}` for a known-existing user → response body contains `"Invalid password"`. [4](#0-3) 
2. `POST /sessions` with `{"email":"doesnotexist@example.com","password":"wrongpass"}` → response body contains the raw `FindUser` datastore error text (distinct wording/format from step 1), since `CreateSession` returns immediately from `FindUser`'s error without normalization. [5](#0-4) 
3. Both requests return the same `401` status from `sessions_controller.go`, but the differing JSON body content (line 28 of `helpers.go` embeds `err.Error()` verbatim) allows an attacker to script enumeration of valid emails against the node. [2](#0-1)

### Citations

**File:** core/web/sessions_controller.go (L56-60)
```go
	sid, err := sc.App.AuthenticationProvider().CreateSession(ctx, sr)
	if err != nil {
		jsonAPIError(c, http.StatusUnauthorized, err)
		return
	}
```

**File:** core/web/helpers.go (L21-29)
```go
func jsonAPIError(c *gin.Context, statusCode int, err error) {
	_ = c.Error(err).SetType(gin.ErrorTypePublic)
	var jsonErr *models.JSONAPIErrors
	if errors.As(err, &jsonErr) {
		c.JSON(statusCode, jsonErr)
		return
	}
	c.JSON(statusCode, models.NewJSONAPIErrorsWith(err.Error()))
}
```

**File:** core/sessions/localauth/orm.go (L144-162)
```go
func (o *orm) CreateSession(ctx context.Context, sr sessions.SessionRequest) (string, error) {
	user, err := o.FindUser(ctx, sr.Email)
	if err != nil {
		return "", err
	}
	lggr := o.lggr.With("user", user.Email)
	lggr.Debugw("Found user")

	// Do email and password check first to prevent extra database look up
	// for MFA tokens leaking if an account has MFA tokens or not.
	if !constantTimeEmailCompare(strings.ToLower(sr.Email), strings.ToLower(user.Email)) {
		o.auditLogger.Audit(audit.AuthLoginFailedEmail, map[string]any{"email": sr.Email})
		return "", pkgerrors.New("Invalid email")
	}

	if !utils.CheckPasswordHash(sr.Password, string(user.HashedPassword)) {
		o.auditLogger.Audit(audit.AuthLoginFailedPassword, map[string]any{"email": sr.Email})
		return "", pkgerrors.New("Invalid password")
	}
```
