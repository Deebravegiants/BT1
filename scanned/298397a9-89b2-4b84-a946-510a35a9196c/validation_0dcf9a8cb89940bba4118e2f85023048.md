Based on my investigation, I found a genuine analog to the reported CWE-943 (Improper Neutralization of Special Elements in Data Query Logic) bug class in the LDAP authentication path.

### Title
LDAP Filter Injection via Unescaped Group Common Name in `FindUser` - ([File: core/sessions/ldapauth/ldap.go])

### Summary
The Kibana CVE describes attacker-controlled input reaching query logic without proper neutralization of special elements, allowing scope/filter manipulation (NoSQL injection analog). In the chainlink LDAP authentication provider, most user-supplied values (emails) are correctly passed through `ldap.EscapeFilter()` before being interpolated into LDAP search filter strings [1](#0-0) , but the group Common Name (CN) values used to build the LDAP search filter in `ldapGroupMembersListToUser` are inserted directly, unescaped, via `fmt.Sprintf` [2](#0-1) .

### Finding Description
`ldapGroupMembersListToUser` (shared by `ListUsers`/`FindUser` role-group listing and the `sync.go` upstream syncer) constructs an LDAP filter as `fmt.Sprintf("(&(cn=%s))", groupNameCN)` with no call to `ldap.EscapeFilter` on `groupNameCN` [3](#0-2) . The `groupNameCN` values originate from node operator configuration (`AdminUserGroupCN`, `EditUserGroupCN`, `RunUserGroupCN`, `ReadUserGroupCN`) rather than end-user input, which limits attacker control under normal operation. In contrast, the email-based filters used elsewhere in the same file are properly escaped with `ldap.EscapeFilter(email)` before insertion into filter strings [1](#0-0) [4](#0-3) .

### Impact Explanation
If an unprivileged, low-trust actor could ever influence a Group CN value that flows into this filter construction (e.g., through an admin-configurable but attacker-reachable field, or future code paths reusing this helper with less-trusted input), LDAP filter injection could allow expanding the scope of the group membership query, potentially returning membership from unintended groups and granting elevated roles (Admin/Edit/Run) to a user who should only have View access — a role/authorization bypass consistent with the reported bug class (unauthorized data disclosure via injected query logic).

### Likelihood Explanation
Likelihood is low-to-moderate as currently wired: `groupNameCN` values are sourced from LDAP driver configuration set by the node operator (`config.LDAP`), not from a per-request unprivileged user input, so a remote unauthenticated/unprivileged attacker cannot directly trigger this through the web API today. This differs from the Kibana CVE's "authenticated user submits crafted input" attack surface. I could not find a currently-reachable unprivileged-actor code path that lets external request data flow into `groupNameCN`; this weakens confidence that it meets the "concrete authentication or role bypass" bar via a purely unprivileged HTTP/gateway request.

### Recommendation
Apply `ldap.EscapeFilter()` to `groupNameCN` before use in `ldapGroupMembersListToUser`'s `filterQuery` construction, consistent with how email values are already escaped elsewhere in this file, to eliminate any injection risk regardless of the CN's current trust level and to guard against future refactors reusing this helper with request-influenced input.

### Proof of Concept
Not applicable as a remotely-triggerable PoC today: `groupNameCN` is not attacker-influenced in the current call graph (it is a static operator-configured value passed to `ldapGroupMembersListToUser` from `ListUsers`, `FindUser`, and `sync.go`) [5](#0-4) . A hypothetical PoC would require a code path exposing group-CN selection to an unprivileged caller, which does not currently exist in this codebase based on my review — this should be validated with full repo access (a Devin session) if a hidden reachable path exists that the index did not surface.

### Citations

**File:** core/sessions/ldapauth/ldap.go (L154-156)
```go
	escapedEmail := ldap.EscapeFilter(email)
	searchBaseDN := fmt.Sprintf("%s, %s", l.config.GroupsDN(), l.config.BaseDN())
	filterQuery := fmt.Sprintf("(&(uniquemember=%s=%s,%s,%s))", l.config.BaseUserAttr(), escapedEmail, l.config.UsersDN(), l.config.BaseDN())
```

**File:** core/sessions/ldapauth/ldap.go (L252-270)
```go
	adminUsers, err := l.ldapGroupMembersListToUser(conn, l.config.AdminUserGroupCN(), sessions.UserRoleAdmin)
	if err != nil {
		l.lggr.Errorf("error in ldapGroupMembersListToUser: %v", err)
		return users, errors.New("unable to list group users")
	}
	// Query for list of uniqueMember IDs present in Edit group
	editUsers, err := l.ldapGroupMembersListToUser(conn, l.config.EditUserGroupCN(), sessions.UserRoleEdit)
	if err != nil {
		l.lggr.Error("error in ldapGroupMembersListToUser: ", err)
		return users, errors.New("unable to list group users")
	}
	// Query for list of uniqueMember IDs present in Run group
	runUsers, err := l.ldapGroupMembersListToUser(conn, l.config.RunUserGroupCN(), sessions.UserRoleRun)
	if err != nil {
		l.lggr.Error("error in ldapGroupMembersListToUser: ", err)
		return users, errors.New("unable to list group users")
	}
	// Query for list of uniqueMember IDs present in Read group
	readUsers, err := l.ldapGroupMembersListToUser(conn, l.config.ReadUserGroupCN(), sessions.UserRoleView)
```

**File:** core/sessions/ldapauth/ldap.go (L666-671)
```go
	filterQuery := "(|"
	for _, email := range emails {
		escapedEmail := ldap.EscapeFilter(email)
		filterQuery = fmt.Sprintf("%s(%s=%s)", filterQuery, l.config.BaseUserAttr(), escapedEmail)
	}
	filterQuery = fmt.Sprintf("(&%s))", filterQuery)
```

**File:** core/sessions/ldapauth/ldap.go (L711-732)
```go
// ldapGroupMembersListToUser queries the LDAP server given a conn for a list of uniqueMember who are part of the parameterized group. Reused by sync.go
func ldapGroupMembersListToUser(
	conn LDAPConn,
	groupNameCN string,
	roleToAssign sessions.UserRole,
	groupsDN string,
	baseDN string,
	queryTimeout time.Duration,
	lggr logger.Logger,
) ([]sessions.User, error) {
	users := []sessions.User{}
	// Prepare and query the GroupsDN for the specified group name
	searchBaseDN := fmt.Sprintf("%s, %s", groupsDN, baseDN)
	filterQuery := fmt.Sprintf("(&(cn=%s))", groupNameCN)
	searchRequest := ldap.NewSearchRequest(
		searchBaseDN,
		ldap.ScopeWholeSubtree, ldap.NeverDerefAliases,
		0, int(queryTimeout.Seconds()), false,
		filterQuery,
		[]string{UniqueMemberAttribute},
		nil,
	)
```
