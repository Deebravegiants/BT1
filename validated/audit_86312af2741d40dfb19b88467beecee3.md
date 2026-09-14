Confirmed the analog pattern: both `AuthorizedUserWithSession` (localauth ORM) and `FindUserByAPIToken` (LDAP/OIDC auth) recompute expiry using the **currently configured duration** applied to the entire elapsed period, rather than the duration that was in effect when the session/token was originally created — the exact same bug class as `_accruedPeriodInterest()` retroactively applying the latest rate to the whole period.

### Title
Session/API-token expiry recomputed with live config duration retroactively applied to the entire token lifetime, allowing already-expired credentials to be revived on a config change — ([File: core/sessions/localauth/orm.go], [File: core/sessions/ldapauth/ldap.go], [File: core/sessions/oidcauth/oidc.go])

### Summary
`findValidSession` in `core/sessions/localauth/orm.go` and `FindUserByAPIToken` in `core/sessions/ldapauth/ldap.go` / `core/sessions/oidcauth/oidc.go` validate session/token freshness with `created_at`/`last_used` plus the *current* `SessionTimeout`/`UserAPITokenDuration` config value, instead of a duration fixed at credential-issuance time. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
Each of these functions runs a SQL check like `created_at + $duration >= now()` (or `last_used + $duration >= now()` for local sessions), where `$duration` is the *currently configured* `SessionTimeout` / `UserAPITokenDuration`, not the value that was configured at the moment the session/token was created. [4](#0-3) [5](#0-4) 

This is structurally identical to the reported `_accruedPeriodInterest()` bug: a time-bounded quantity (interest accrual / credential validity) is computed by applying whatever rate/duration is configured *right now* to the entire historical period, rather than segmenting by when the configuration was actually in effect. Just as a curator's `performanceFeeRate` change retroactively re-prices the whole accrual period, an admin's `UserAPITokenDuration`/`SessionTimeout` change here retroactively re-validates (or re-invalidates) every existing session/token, because there is no stored, fixed expiry timestamp — only a floating "duration applied against creation time" recomputed on every check. [6](#0-5) 

The practical consequence: if an operator *increases* `UserAPITokenDuration` (e.g., from 240h to a larger value) for any legitimate reason, every previously issued API token that had already crossed its originally-intended expiry window under the old setting is silently revalidated the next time an unprivileged holder of that stale token calls the authenticated node API (`AuthenticateByToken` → `FindUserByAPIToken`), because the check only compares `created_at + newDuration` against `now()`. [7](#0-6) 

Since there is no persisted absolute expiry, a token/session's effective lifetime is not fixed at issuance — it is a function of whatever the *global* duration setting happens to be at request time. Any unprivileged client presenting a previously-issued (and, under the config at issuance time, already expired) API token or session cookie is retroactively re-authenticated the moment the operator widens the duration setting, with no re-issuance or re-login required.

### Impact Explanation
This is an authentication-bypass-adjacent flaw: credentials intended to expire under the security posture in effect when they were issued can be silently revived by an unrelated, later config change, defeating the security guarantee that `UserAPITokenDuration`/`SessionTimeout` reductions/increases are meant to provide. It affects `AuthenticateByToken` and `AuthenticateBySession`, which gate the entire authenticated Node API surface (`core/web/router.go` `authv2` routes), so a stale/leaked credential believed to be expired can regain full API access. [8](#0-7) 

### Likelihood Explanation
Likelihood is Medium: it requires an operator to change `WebServer.SessionTimeout`, `WebServer.LDAP.UserAPITokenDuration`, or `WebServer.OIDC.UserAPITokenDuration` (increase or in some ordering, decrease) — a legitimate, expected admin action — after which any unprivileged holder of an old/leaked/expired credential automatically benefits on their very next request, with no additional action needed from them. [9](#0-8) 

### Recommendation
Persist an absolute `expires_at` timestamp on session/token creation (computed from the duration in effect at issuance time) instead of recomputing validity from `created_at`/`last_used` plus the live config duration on every check. Validity should then be `expires_at >= now()`, which is immune to later duration config changes, mirroring the report's recommendation to segment/fix values at the time they are established rather than re-applying the current configuration retroactively.

### Proof of Concept
1. Operator sets `UserAPITokenDuration = '1h'`. A user's API token is issued at `T0`.
2. At `T0 + 2h`, the token is expired under the original 1h policy; the client's request would be rejected by `FindUserByAPIToken`. [10](#0-9) 
3. Operator changes `UserAPITokenDuration` to `'240h'` for unrelated reasons (e.g., convenience for a different team).
4. The same client retries with the same old token at `T0 + 2h + ε`. `FindUserByAPIToken` now evaluates `created_at + 240h >= now()`, which is true, and the request is authenticated successfully — even though the token was already expired under the policy at issuance/first-failure time. [11](#0-10)

### Citations

**File:** core/sessions/localauth/orm.go (L68-75)
```go
// findValidSession finds an unexpired session by its ID and returns the associated email.
func (o *orm) findValidSession(ctx context.Context, sessionID string) (email string, err error) {
	if err := o.ds.GetContext(ctx, &email, "SELECT email FROM sessions WHERE id = $1 AND last_used + $2 >= now() FOR UPDATE", sessionID, o.sessionDuration); err != nil {
		o.lggr.Infof("query result: %v", email)
		return email, pkgerrors.Wrap(err, "no matching user for provided session token")
	}
	return email, nil
}
```

**File:** core/sessions/ldapauth/ldap.go (L217-221)
```go
	}
	err := l.ds.GetContext(ctx, &foundUserToken,
		"SELECT user_email, user_role, created_at + $2 >= now() as valid FROM ldap_user_api_tokens WHERE token_key = $1",
		apiToken, l.config.UserAPITokenDuration().Duration(),
	)
```

**File:** core/sessions/oidcauth/oidc.go (L297-326)
```go
// FindUserByAPIToken retrieves a possible stored user and role from the oidc_user_api_tokens table store
func (oi *oidcAuthenticator) FindUserByAPIToken(ctx context.Context, apiToken string) (clsessions.User, error) {
	if !oi.config.UserAPITokenEnabled() {
		return clsessions.User{}, errors.New("API token is not enabled")
	}

	var foundUser clsessions.User
	err := sqlutil.TransactDataSource(ctx, oi.ds, nil, func(tx sqlutil.DataSource) error {
		// Query the oidc user API token table for given token, user role and email are cached so
		// no further upstream OIDC query is performed, sessions and tokens are synced against the upstream server
		// via the UpstreamSyncInterval config and reaper.go sync implementation
		var foundUserToken struct {
			UserEmail string
			UserRole  clsessions.UserRole
			Valid     bool
		}
		if err := tx.GetContext(ctx, &foundUserToken,
			"SELECT user_email, user_role, created_at + $2 >= now() as valid FROM oidc_user_api_tokens WHERE token_key = $1",
			apiToken, oi.config.UserAPITokenDuration().Duration(),
		); err != nil {
			return err
		}
		if !foundUserToken.Valid {
			return clsessions.ErrUserSessionExpired
		}
		foundUser = clsessions.User{
			Email: foundUserToken.UserEmail,
			Role:  foundUserToken.UserRole,
		}
		return nil
```

**File:** core/web/auth/auth.go (L41-45)
```go
	AuthorizedUserWithSession(ctx context.Context, sessionID string) (clsessions.User, error)
	FindExternalInitiator(ctx context.Context, eia *auth.Token) (*bridges.ExternalInitiator, error)
	FindUser(ctx context.Context, email string) (clsessions.User, error)
	FindUserByAPIToken(ctx context.Context, apiToken string) (clsessions.User, error)
}
```

**File:** core/web/auth/auth.go (L78-99)
```go
func AuthenticateByToken(c *gin.Context, authr Authenticator) error {
	ctx := c.Request.Context()
	token := &auth.Token{
		AccessKey: c.GetHeader(APIKey),
		Secret:    c.GetHeader(APISecret),
	}
	if token.AccessKey == "" {
		return auth.ErrorAuthFailed
	}

	if token.Secret == "" {
		return auth.ErrorAuthFailed
	}

	// We need to first load the user row so we can compare tokens using the stored salt
	user, err := authr.FindUserByAPIToken(ctx, token.AccessKey)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) || errors.Is(err, clsessions.ErrUserSessionExpired) {
			return auth.ErrorAuthFailed
		}
		return err
	}
```

**File:** core/config/docs/core.toml (L765-776)
```text
# Debug enables printing of Sentry SDK debug messages.
Debug = false # Default
# DSN is the data source name where events will be sent. Sentry is completely disabled if this is left blank.
DSN = 'sentry-dsn' # Example
# Environment overrides the Sentry environment to the given value. Otherwise autodetects between dev/prod.
Environment = 'my-custom-env' # Example
# Release overrides the Sentry release to the given value. Otherwise uses the compiled-in version number.
Release = 'v1.2.3' # Example


# Insecure config family is only allowed in development builds.
[Insecure]
```
