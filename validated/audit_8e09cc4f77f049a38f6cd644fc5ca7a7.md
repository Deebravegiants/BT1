### Title
OIDC Role Claims Matched by Display Name Instead of Immutable Group ID Enables Privilege Escalation - (File: core/sessions/oidcauth/oidc.go)

### Summary
Chainlink's node WebServer OIDC authentication maps a user's role (`Admin`/`Edit`/`Run`/`View`) by doing a literal string match between the ID token's group claim values and admin-configured group *names* (`AdminClaim`, `EditClaim`, `RunClaim`, `ReadClaim`), rather than matching against an immutable, provider-issued group object ID. This is the exact bug class described in CVE-2025-49012 (himmelblau's `pam_allow_groups`): trusting a mutable, human-readable group display name for access control instead of a unique identifier allows any user who can create/join a same-named group at the identity-provider level to be granted elevated roles.

### Finding Description
`NewOIDCAuthenticator` requires operators to configure RBAC role mappings as plain group *name* strings: [1](#0-0) 

During the `/oidc-exchange` callback, the server extracts the raw string values of the configured claim (default name `groups`, see `ClaimName = 'groups' # Default`) directly from the ID token and passes them, unmodified, into role resolution: [2](#0-1) 

Role resolution then performs a simple `slices.Contains` string-equality check between the returned claim values and the configured claim names, with no reference to any stable, provider-issued object identifier: [3](#0-2) 

`ExtractIDClaimValues` further confirms that the claim is expected to be a plain string or array of strings (group names), not GUIDs/object IDs: [4](#0-3) 

This mirrors the LDAP path (`ldapauth`), which resolves roles from LDAP group `cn` (common name, also a display name) rather than an immutable directory GUID: [5](#0-4) 

If the configured identity provider (e.g., Azure Entra ID / Microsoft Graph, many self-service IdPs, or any OIDC provider that allows non-admin users to create groups) permits creation of multiple groups with the same display name — which is exactly the condition documented in CVE-2025-49012 — then an unprivileged, low-privilege user can:
1. Create (or get added to) a group whose name matches the configured `AdminClaim`/`EditClaim`/`RunClaim` value (e.g. `NodeAdmins`).
2. Authenticate through the standard `/oidc-login` → `/oidc-exchange` flow.
3. Have the resulting ID token's `groups` claim contain the attacker-created group's display name.
4. Be granted the corresponding elevated `UserRole` (e.g., `UserRoleAdmin`) by `IDClaimsToUserRole`, since it only checks name equality.

This is a bypass reachable purely through the node's public-facing WebServer authentication endpoints — no operator/administrator action is required from the attacker's side, only misuse of self-service group creation on the external IdP (a realistic, commonly-permitted tenant configuration, as documented in the reference advisory).

### Impact Explanation
A successful exploitation grants an unauthorized session with `UserRoleAdmin` (or `Edit`/`Run`) on the Chainlink node's WebServer/API — full administrative control over the node (job specs, keys management endpoints, bridges, etc.), constituting a concrete authentication/role bypass. This matches the "concrete authentication or role bypass" acceptance criterion.

### Likelihood Explanation
Likelihood is Medium: it requires that the operator's chosen OIDC identity provider allows self-service creation of groups (or subscription to groups) with attacker-controlled display names matching the operator's configured `AdminClaim`/`EditClaim`/`RunClaim`/`ReadClaim` strings. Many enterprise/cloud IdPs (as documented in the referenced Microsoft/Entra ID discussion) permit this by default for non-admin users, so the precondition is realistic and not purely theoretical, matching the exact scenario disclosed for himmelblau.

### Recommendation
Deprecate/remove name-based group matching for `AdminClaim`/`EditClaim`/`RunClaim`/`ReadClaim` (and the analogous LDAP `*UserGroupCN` settings), and instead require and match against the identity provider's immutable group object ID (e.g., Azure AD `objectId`/`oid`, or a `groups` claim configured to emit `sub`/object IDs rather than display names). At minimum, document prominently that operators must configure their IdP to emit group object IDs in the claim (or restrict group creation to admins) and that display-name-based claims are inherently spoofable.

### Proof of Concept
1. Configure `WebServer.OIDC.AdminClaim = 'NodeAdmins'` and use an IdP (e.g., Entra ID) whose tenant permits non-admin users to create Microsoft 365/security groups.
2. As a low-privileged user, create a new group named exactly `NodeAdmins` via the Graph API/self-service portal and add yourself as a member.
3. Log in to the Chainlink node via `/oidc-login`, complete the OIDC flow, and let `/oidc-exchange` process the callback: the ID token's `groups` claim will include the attacker-created `NodeAdmins` group name.
4. `IDClaimsToUserRole` (`core/sessions/oidcauth/oidc.go:599-618`) matches this name against `AdminClaim` and returns `UserRoleAdmin`, and a corresponding admin session is stored via the `oidc_sessions` insert at `core/sessions/oidcauth/oidc.go:247-260`, granting the attacker a fully privileged node session.

### Citations

**File:** core/sessions/oidcauth/oidc.go (L75-80)
```go
	// Ensure all RBAC role mappings to OIDC Id claims are defined, and required fields populated, or error on startup
	lggr.Debugf("OIDC CFG:\n %#v\n", oidcCfg)
	if oidcCfg.AdminClaim() == "" || oidcCfg.EditClaim() == "" ||
		oidcCfg.RunClaim() == "" || oidcCfg.ReadClaim() == "" {
		return nil, errors.New("OIDC Group name mapping for callback group claims for all local RBAC role required. Set group names for `_Claim` fields")
	}
```

**File:** core/sessions/oidcauth/oidc.go (L220-245)
```go
	idClaims, err := oi.ExtractIDClaimValues(claims, oi.config.ClaimName())
	if err != nil {
		oi.lggr.Errorf("Failed to extract ID claims from ID token. ClaimName: '%s': error %v", oi.config.ClaimName(), err)
		c.String(http.StatusInternalServerError, "Failed to extract ID claims from claims")
		return
	}
	email, ok := claims["email"].(string)
	if !ok {
		oi.lggr.Errorf("Failed to get email from claims. error: %v", err)
		c.String(http.StatusInternalServerError, "Failed to get email from claims")
	}
	oi.lggr.Tracef("Received and validated ID claims: %v\n", idClaims)

	// Map the claims to a role and insert a newly created session paired with role mapping for user
	role, err := oi.IDClaimsToUserRole(
		idClaims,
		oi.config.AdminClaim(),
		oi.config.EditClaim(),
		oi.config.RunClaim(),
		oi.config.ReadClaim(),
	)
	if err != nil {
		oi.lggr.Errorf("Failed to map configured RBAC role name against received list of group claims: %v", err)
		c.String(http.StatusBadRequest, "No matching role within attested user group claims")
		return
	}
```

**File:** core/sessions/oidcauth/oidc.go (L599-618)
```go
func (oi *oidcAuthenticator) IDClaimsToUserRole(idClaims []string, adminClaim string, editClaim string, runClaim string, readClaim string) (clsessions.UserRole, error) {
	// If defined Admin group name is present in id claims, return UserRoleAdmin
	if slices.Contains(idClaims, adminClaim) {
		return clsessions.UserRoleAdmin, nil
	}
	// Check edit role
	if slices.Contains(idClaims, editClaim) {
		return clsessions.UserRoleEdit, nil
	}
	// Check run role
	if slices.Contains(idClaims, runClaim) {
		return clsessions.UserRoleRun, nil
	}
	// Check view role
	if slices.Contains(idClaims, readClaim) {
		return clsessions.UserRoleView, nil
	}
	// No role group found, error
	return clsessions.UserRoleView, ErrUserNoOIDCGroups
}
```

**File:** core/sessions/oidcauth/oidc.go (L621-646)
```go
func (oi *oidcAuthenticator) ExtractIDClaimValues(claims map[string]any, key string) ([]string, error) {
	claimValues, ok := claims[key]
	if !ok {
		return nil, fmt.Errorf("claim '%s' not found in ID token", key)
	}

	// Handle different types of claim values
	switch v := claimValues.(type) {
	case []any:
		val := make([]string, 0, len(v))
		for _, item := range v {
			str, ok := item.(string)
			if !ok {
				return nil, fmt.Errorf("invalid type for item in '%s': expected string, got %T", key, item)
			}
			val = append(val, str)
		}
		return val, nil
	case []string:
		return v, nil
	case string:
		return []string{v}, nil
	default:
		return nil, fmt.Errorf("claim '%s' is not a string or array: got %T", key, v)
	}
}
```

**File:** core/sessions/ldapauth/ldap.go (L785-811)
```go
func GroupSearchResultsToUserRole(ldapGroups []*ldap.Entry, adminCN string, editCN string, runCN string, readCN string) (sessions.UserRole, error) {
	// If defined Admin group name is present in groups search result, return UserRoleAdmin
	for _, group := range ldapGroups {
		if group.GetAttributeValue("cn") == adminCN {
			return sessions.UserRoleAdmin, nil
		}
	}
	// Check edit role
	for _, group := range ldapGroups {
		if group.GetAttributeValue("cn") == editCN {
			return sessions.UserRoleEdit, nil
		}
	}
	// Check run role
	for _, group := range ldapGroups {
		if group.GetAttributeValue("cn") == runCN {
			return sessions.UserRoleRun, nil
		}
	}
	// Check view role
	for _, group := range ldapGroups {
		if group.GetAttributeValue("cn") == readCN {
			return sessions.UserRoleView, nil
		}
	}
	// No role group found, error
	return sessions.UserRoleView, ErrUserNoLDAPGroups
```
