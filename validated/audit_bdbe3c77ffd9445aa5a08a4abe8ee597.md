Audit Report

## Title
LDAP Injection via unsanitized Bind DN construction in `CreateSession`/`TestPassword` (LDAP filter-escaping used where DN-escaping is required) - (File: core/sessions/ldapauth/ldap.go)

## Summary
The LDAP authentication driver constructs the bind DN for login by concatenating the user-supplied `sr.Email` field, after passing it only through `ldap.EscapeFilter` (RFC 4515 filter-escaping), into a DN string via `fmt.Sprintf("%s=%s,%s,%s", ...)`. `ldap.EscapeFilter` does not escape DN metacharacters (`,`, `+`, `"`, `;`, `<`, `>`), so an attacker-controlled email value can alter the structure of the DN bound against the upstream LDAP server.

## Finding Description
`CreateSession` builds the bind DN as `searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())` using `escapedEmail := ldap.EscapeFilter(strings.ToLower(sr.Email))`, then calls `conn.Bind(searchBaseDN, sr.Password)`. [1](#0-0)  The identical pattern exists in `TestPassword`. [2](#0-1)  `ldap.EscapeFilter` is designed for search-filter contexts, not DN contexts, so it fails to neutralize DN-structural characters. The `/sessions` endpoint binds the raw JSON body directly into `sessions.SessionRequest` and calls `CreateSession` without any `ValidateEmail`-style check, which is only invoked during local admin user creation (`NewUser`), not at login. [3](#0-2) [4](#0-3)  This confirms an unauthenticated caller can submit an arbitrary string as `Email` to `/sessions`, which then flows unsanitized (with respect to DN syntax) into the bind DN.

## Impact Explanation
This maps to the "node API authentication/role bypass" and "gateway/identity request impersonation" impact classes: a crafted `Email` value can, depending on the target directory's tree layout, cause the bind to resolve against an unintended DN rather than the operator-configured `BaseUserAttr`/`UsersDN`/`BaseDN` structure. This is a genuine escaping-context defect (using filter-escaping where DN-escaping is required) rather than a hypothetical or best-practice-only issue.

## Likelihood Explanation
The vulnerable code is only reachable when the node is configured with `AuthenticationMethod = 'ldap'`, gated by config validation. [5](#0-4)  Given that configuration, the `/sessions` endpoint is reachable by any unauthenticated client, and successful exploitation additionally depends on the specific LDAP directory's structure/contents (whether an attacker-crafted DN suffix resolves to a real bindable object) — so likelihood is conditional but the code-level flaw itself is concrete and demonstrable via review, not speculative.

## Recommendation
Do not concatenate user input directly into a DN. Use DN-escaping (escaping `,`, `+`, `"`, `\`, `<`, `>`, `;`, leading/trailing spaces, leading `#`) for DN components, or better, resolve the user's DN via a filtered `Search` (where `ldap.EscapeFilter` is correctly applied) and then `Bind` using the DN returned by the directory server rather than any client-supplied value. Apply the same fix to `CreateSession`, `TestPassword`, and review `FindUser` and `sync.go`'s bind construction for the same pattern. [6](#0-5) 

## Proof of Concept
1. Deploy a Chainlink node with `AuthenticationMethod = 'ldap'` and configured `BaseDN`/`UsersDN`/`BaseUserAttr`.
2. POST to `/sessions` with a JSON body such as `{"email": "<value containing DN metacharacters like a comma and RDN components>", "password": "<value>"}`.
3. Observe the resulting bind DN constructed at `core/sessions/ldapauth/ldap.go:407` contains attacker-influenced DN structure because `ldap.EscapeFilter` does not neutralize DN metacharacters, and verify against a test/sandbox LDAP server whether the bind resolves to an unintended DN.

### Citations

**File:** core/sessions/ldapauth/ldap.go (L405-411)
```go
	// Attempt to LDAP Bind with user provided credentials
	escapedEmail := ldap.EscapeFilter(strings.ToLower(sr.Email))
	searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
	if err = conn.Bind(searchBaseDN, sr.Password); err != nil {
		l.lggr.Infof("Error binding user authentication request in LDAP Bind: %v", err)
		returnErr = errors.New("unable to log in with LDAP server. Check credentials")
	}
```

**File:** core/sessions/ldapauth/ldap.go (L511-514)
```go
	// Attempt to LDAP Bind with user provided credentials
	escapedEmail := ldap.EscapeFilter(strings.ToLower(email))
	searchBaseDN := fmt.Sprintf("%s=%s,%s,%s", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
	err = conn.Bind(searchBaseDN, password)
```

**File:** core/web/sessions_controller.go (L34-55)
```go
	session := sessions.Default(c)
	var sr clsessions.SessionRequest
	if err := c.ShouldBindJSON(&sr); err != nil {
		jsonAPIError(c, http.StatusBadRequest, fmt.Errorf("error binding json %w", err))
		return
	}

	// Does this user have 2FA enabled?
	userWebAuthnTokens, err := sc.App.AuthenticationProvider().GetUserWebAuthn(ctx, sr.Email)
	if err != nil {
		sc.App.GetLogger().Errorf("Error loading user WebAuthn data: %s", err)
		jsonAPIError(c, http.StatusInternalServerError, errors.New("internal Server Error"))
		return
	}

	// If the user has registered MFA tokens, then populate our session store and context
	// required for successful WebAuthn authentication
	if len(userWebAuthnTokens) > 0 {
		sr.SessionStore = sc.sessions
		sr.WebAuthnConfig = sc.App.GetWebAuthnConfiguration()
	}

```

**File:** core/sessions/user.go (L41-66)
```go
// NewUser creates a new user by hashing the passed plainPwd with bcrypt.
func NewUser(email string, plainPwd string, role UserRole) (User, error) {
	if err := ValidateEmail(email); err != nil {
		return User{}, err
	}

	pwd, err := ValidateAndHashPassword(plainPwd)
	if err != nil {
		return User{}, err
	}

	return User{
		Email:          email,
		HashedPassword: *config.NewSecretString(pwd),
		Role:           role,
	}, nil
}

// ValidateEmail is the single point of logic for user email validations
func ValidateEmail(email string) error {
	if len(email) == 0 {
		return pkgerrors.New("Must enter an email")
	}
	_, err := mail.ParseAddress(email)
	return err
}
```

**File:** core/config/toml/types.go (L1150-1153)
```go
	switch *w.AuthenticationMethod {
	case string(sessions.LDAPAuth):
		// Assert LDAP fields when AuthMethod set to LDAP
		if *w.LDAP.BaseDN == "" {
```

**File:** core/sessions/ldapauth/sync.go (L126-130)
```go
	// Root level root user auth with credentials provided from config
	bindStr := l.config.BaseUserAttr() + "=" + l.config.ReadOnlyUserLogin() + "," + l.config.BaseDN()
	if err = conn.Bind(bindStr, l.config.ReadOnlyUserPass()); err != nil {
		l.lggr.Error("Unable to login as initial root LDAP user: ", err)
	}
```
