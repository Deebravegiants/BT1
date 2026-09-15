I found a genuine analog. The OIDC authentication provider caches the user's role in the local `oidc_sessions` table at session creation and never re-validates it against the upstream identity provider on subsequent requests — unlike the LDAP provider, whose own doc comments explicitly state role/session sync happens "for every auth endpoint hit" in addition to interval-based sync via `sync.go`.

### Title
Stale cached role/session authorization in OIDC authenticator allows continued elevated API access after upstream permission revocation - (File: core/sessions/oidcauth/oidc.go)

### Summary
The `oidcAuthenticator.AuthorizedUserWithSession` function validates a session purely by checking the local `oidc_sessions` table for expiry, returning the role that was cached at login time, with no revalidation against the upstream OIDC identity provider on the request path.

### Finding Description
`AuthorizedUserWithSession` queries `oidc_sessions` for `user_email`, `user_role`, and expiry validity, then directly returns a `clsessions.User` built from those cached fields <cite repo="Alyssadaypin/chainlink--010" path="core/sessions/oidcauth/oidc.go" start="349="/> [1](#0-0) . This role was written once during the login/token-exchange flow when ID-token claims were mapped to a role via `IDClaimsToUserRole`, and is never re-checked against the identity provider on subsequent requests through this code path. This contrasts with the LDAP authenticator, whose package doc explicitly states: "User session and roles are cached and revalidated with the upstream service... This sync happens for every auth endpoint hit, and via the defined sync interval" [2](#0-1) , and whose `AuthorizedUserWithSession` similarly only reads the cached role from `ldap_sessions`, relying on a separate background `LDAPServerStateSyncer.Work` reconciliation job [3](#0-2) . No equivalent background reconciliation job exists for OIDC in this codebase (`grep` for sync/reaper logic in `oidc.go` returns nothing beyond the two config option matches) [4](#0-3) . The router applies role checks (`RequiresEditRole`, `RequiresAdminRole`) purely against this cached, potentially stale `User.Role` value carried in the gin context [5](#0-4) .

Sessions persist for `WebServer.OIDC.SessionTimeout` (default `15m0s`) and API tokens for `UserAPITokenDuration` (default `240h0m0s`, i.e. 10 days) [6](#0-5) . During these windows, a user whose group membership/claims are revoked or downgraded upstream (e.g., removed from `NodeAdmins`) retains their prior elevated role inside the chainlink node — mirroring the GitLab CVE-2019-19312 pattern where a previously-privileged consumer continued to retrieve privileged data after the upstream authorization state changed, because the check relied on stale cached state rather than the current source of truth.

### Impact Explanation
An operator who revokes or downgrades a user's OIDC group membership (removing admin/edit access) cannot immediately cut off that user's node access; the user's existing session or, more significantly, their long-lived API token (up to 10 days) continues to authorize privileged operations — job creation/deletion, key export, bridge management — via `RequiresAdminRole`/`RequiresEditRole` gated routes [7](#0-6) , contradicting the intent of the upstream deprovisioning action.

### Likelihood Explanation
This requires an operator-driven revocation event (e.g., offboarding, role downgrade) followed by continued use of an already-issued, unexpired session cookie or API token by the affected account. It is a realistic, not contrived, sequence for any deployment using `WebServer.AuthenticationMethod = oidc`, and requires no attacker sophistication beyond already possessing a previously valid credential.

### Recommendation
Add per-request (or short-interval) revalidation of OIDC claims/role against the identity provider (or a background sync similar to `ldapauth`'s `LDAPServerStateSyncer`) so that role downgrades and revocations propagate promptly to `oidc_sessions` and `oidc_user_api_tokens`, rather than only being enforced at next login or full session/token expiry.

### Proof of Concept
1. Configure node with `WebServer.AuthenticationMethod = oidc`, mapping `NodeAdmins` group to admin role.
2. User logs in while a member of `NodeAdmins`; `oidc_sessions` row is created with `user_role = admin` [8](#0-7) .
3. Operator removes the user from `NodeAdmins` in the upstream identity provider.
4. User continues making requests with the still-valid session cookie (or a previously issued API token) within `SessionTimeout`/`UserAPITokenDuration`; `AuthorizedUserWithSession`/`FindUserByAPIToken` return the stale cached `admin` role, and `RequiresAdminRole`-protected endpoints (e.g., key export, job deletion) succeed despite the upstream revocation.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L1-80)
```go
/*
The OIDC module handles authentication by redirecting to a
Open ID Connect Identity Provider.
*/
package oidcauth

import (
	"context"
	"crypto/rand"
	"crypto/subtle"
	"database/sql"
	"encoding/base64"
	"errors"
	"fmt"
	"io"
	"log"
	"net/http"
	"slices"
	"strings"

	"github.com/coreos/go-oidc/v3/oidc"
	"github.com/gin-contrib/sessions"
	"github.com/gin-gonic/gin"
	"golang.org/x/oauth2"

	"github.com/smartcontractkit/chainlink-common/pkg/sqlutil"
	"github.com/smartcontractkit/chainlink-common/pkg/utils/mathutil"
	"github.com/smartcontractkit/chainlink/v2/core/auth"
	"github.com/smartcontractkit/chainlink/v2/core/bridges"
	"github.com/smartcontractkit/chainlink/v2/core/config"
	"github.com/smartcontractkit/chainlink/v2/core/logger"
	"github.com/smartcontractkit/chainlink/v2/core/logger/audit"
	clsessions "github.com/smartcontractkit/chainlink/v2/core/sessions"
	"github.com/smartcontractkit/chainlink/v2/core/utils"
	webauth "github.com/smartcontractkit/chainlink/v2/core/web/auth"
)

const (
	SQLSelectUserbyEmail = "SELECT * FROM users WHERE lower(email) = lower($1)"
)

var ErrUserNoOIDCGroups = errors.New("user claims response from identity server received, but no matching role group names in claim")

type oidcAuthenticator struct {
	ds           sqlutil.DataSource
	config       config.OIDC
	provider     *oidc.Provider
	oidcConfig   *oidc.Config
	oauth2Config *oauth2.Config
	lggr         logger.Logger
	auditLogger  audit.AuditLogger
}

// ExchangeTokenRequest represents the expected JSON payload from the frontend
type ExchangeTokenRequest struct {
	Code  string `json:"code" binding:"required"`
	State string `json:"state"`
}

// ExchangeTokenResponse represents the response sent to the frontend
type ExchangeTokenResponse struct {
	Success bool   `json:"success"`
	Message string `json:"message,omitempty"`
}

// oidcAuthenticator implements sessions.AuthenticationProvider interface
var _ clsessions.AuthenticationProvider = (*oidcAuthenticator)(nil)

func NewOIDCAuthenticator(
	ds sqlutil.DataSource,
	oidcCfg config.OIDC,
	lggr logger.Logger,
	auditLogger audit.AuditLogger,
) (*oidcAuthenticator, error) {
	// Ensure all RBAC role mappings to OIDC Id claims are defined, and required fields populated, or error on startup
	lggr.Debugf("OIDC CFG:\n %#v\n", oidcCfg)
	if oidcCfg.AdminClaim() == "" || oidcCfg.EditClaim() == "" ||
		oidcCfg.RunClaim() == "" || oidcCfg.ReadClaim() == "" {
		return nil, errors.New("OIDC Group name mapping for callback group claims for all local RBAC role required. Set group names for `_Claim` fields")
	}
```

**File:** core/sessions/oidcauth/oidc.go (L351-391)
```go
func (oi *oidcAuthenticator) AuthorizedUserWithSession(ctx context.Context, sessionID string) (clsessions.User, error) {
	if len(sessionID) == 0 {
		return clsessions.User{}, errors.New("session ID cannot be empty")
	}
	var foundUser clsessions.User
	err := sqlutil.TransactDataSource(ctx, oi.ds, nil, func(tx sqlutil.DataSource) error {
		// Query the oidc_sessions table for given session ID, user role and email are saved after the id claims is provided and validated
		var foundSession struct {
			UserEmail string
			UserRole  clsessions.UserRole
			Valid     bool
		}
		if err := tx.GetContext(ctx, &foundSession,
			"SELECT user_email, user_role, created_at + $2 >= now() as valid FROM oidc_sessions WHERE id = $1",
			sessionID, oi.config.SessionTimeout().Duration(),
		); err != nil {
			if errors.Is(err, sql.ErrNoRows) {
				return clsessions.ErrUserSessionExpired
			}
			return err
		}
		if !foundSession.Valid {
			// Sessions expired, purge
			return clsessions.ErrUserSessionExpired
		}
		foundUser = clsessions.User{
			Email: foundSession.UserEmail,
			Role:  foundSession.UserRole,
		}
		return nil
	})
	if err != nil {
		if errors.Is(err, clsessions.ErrUserSessionExpired) {
			if _, execErr := oi.ds.ExecContext(ctx, "DELETE FROM oidc_sessions WHERE id = $1", sessionID); execErr != nil {
				oi.lggr.Errorf("error purging stale OIDC session: %v", execErr)
			}
		}
		return clsessions.User{}, err
	}
	return foundUser, nil
}
```

**File:** core/sessions/ldapauth/ldap.go (L12-17)
```go
User session and roles are cached and revalidated with the upstream service at the interval defined in
the local LDAP config through the Application.sessionReaper implementation in reaper.go.

Changes to the upstream identity server will propagate through and update local tables (web sessions, API tokens)
by either removing the entries or updating the roles. This sync happens for every auth endpoint hit, and
via the defined sync interval. One goroutine is created to coordinate the sync timing in the New function
```

**File:** core/sessions/ldapauth/ldap.go (L342-373)
```go
// AuthorizedUserWithSession will return the API user associated with the Session ID if it
// exists and hasn't expired, and update session's LastUsed field. The state of the upstream LDAP server
// is polled and synced at the defined interval via a SleeperTask
func (l *ldapAuthenticator) AuthorizedUserWithSession(ctx context.Context, sessionID string) (sessions.User, error) {
	if len(sessionID) == 0 {
		return sessions.User{}, errors.New("session ID cannot be empty")
	}
	// Query the ldap_sessions table for given session ID, user role and email are cached so
	// no further upstream LDAP query is performed
	var foundSession struct {
		UserEmail string
		UserRole  sessions.UserRole
		Valid     bool
	}
	if err := l.ds.GetContext(ctx, &foundSession,
		"SELECT user_email, user_role, created_at + $2 >= now() as valid FROM ldap_sessions WHERE id = $1",
		sessionID, l.config.SessionTimeout().Duration(),
	); err != nil {
		return sessions.User{}, sessions.ErrUserSessionExpired
	}
	if !foundSession.Valid {
		// Sessions expired, purge
		if _, execErr := l.ds.ExecContext(ctx, "DELETE FROM ldap_sessions WHERE id = $1", sessionID); execErr != nil {
			l.lggr.Errorf("error purging stale ldap session: %v", execErr)
		}
		return sessions.User{}, sessions.ErrUserSessionExpired
	}
	return sessions.User{
		Email: foundSession.UserEmail,
		Role:  foundSession.UserRole,
	}, nil
}
```

**File:** core/web/auth/auth.go (L217-253)
```go
// RequiresEditRole extracts the user object from the context, and asserts the user's role is at least
// 'edit'
func RequiresEditRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role == clsessions.UserRoleView || user.Role == clsessions.UserRoleRun {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("Unauthorized"))
			return
		}
		handler(c)
	}
}

// RequiresAdminRole extracts the user object from the context, and asserts the user's role is 'admin'
func RequiresAdminRole(handler func(*gin.Context)) func(*gin.Context) {
	return func(c *gin.Context) {
		user, ok := GetAuthenticatedUser(c)
		if !ok {
			c.Abort()
			jsonAPIError(c, http.StatusUnauthorized, errors.New("not a valid session"))
			return
		}
		if user.Role != clsessions.UserRoleAdmin {
			c.Abort()
			addForbiddenErrorHeaders(c, "admin", string(user.Role), user.Email)
			jsonAPIError(c, http.StatusForbidden, errors.New("Forbidden"))
			return
		}
		handler(c)
	}
}
```

**File:** core/config/docs/core.toml (L228-233)
```text
# SessionTimeout determines the amount of idle time to elapse before session cookies expire. This signs out GUI users from their sessions.
SessionTimeout = '15m0s' # Default
# UserAPITokenEnabled enables the users to issue API tokens with the same access of their role
UserAPITokenEnabled = false # Default
# UserAPITokenDuration is the duration of time an API token is active for before expiring
UserAPITokenDuration = '240h0m0s' # Default
```

**File:** core/web/router.go (L391-396)
```go
		jc := JobsController{app}
		authv2.GET("/jobs", paginatedRequest(jc.Index))
		authv2.GET("/jobs/:ID", jc.Show)
		authv2.POST("/jobs", auth.RequiresEditRole(jc.Create))
		authv2.PUT("/jobs/:ID", auth.RequiresEditRole(jc.Update))
		authv2.DELETE("/jobs/:ID", auth.RequiresEditRole(jc.Delete))
```
