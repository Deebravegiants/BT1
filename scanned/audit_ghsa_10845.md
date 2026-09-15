# [H] Vikunja Allows Disabled/Locked User Accounts to Authenticate via API Tokens, CalDAV, and OpenID Connect

## Summary
Severity: High
Advisory: GHSA-94xm-jj8x-3cr4
CVE: CVE-2026-33668
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-25
Source: https://github.com/advisories/GHSA-94xm-jj8x-3cr4
Type: github-advisory

## Affected
- Go: `code.vikunja.io/api` — affected >=0.18.0 <2.2.1

## Details
## Summary

When a user account is disabled or locked, the status check is only enforced on the local login and JWT token refresh paths. Three other authentication paths — API tokens, CalDAV basic auth, and OpenID Connect — do not verify user status, allowing disabled or locked users to continue accessing the API and syncing data.

## Details

User status (`StatusDisabled`, `StatusAccountLocked`) is checked in only two places:

1. **Local/LDAP login** (`pkg/routes/api/v1/login.go:74`) — prevents issuing new JWTs
2. **JWT token refresh** (`pkg/routes/api/v1/login.go:247`) — prevents refreshing expired JWTs

Three other authentication paths fetch the user from the database via `GetUserByID` but never inspect the returned user's status:

### 1. API Token Authentication (`pkg/routes/api_tokens.go:76-103`)

API tokens are long-lived (up to years) and have no refresh cycle. A disabled user's API tokens remain fully functional until they expire naturally.

### 2. CalDAV Basic Auth (`pkg/routes/caldav/auth.go`)

The CalDAV basic auth handler validates credentials but does not check user status before granting access. A disabled user with valid credentials or a CalDAV token can continue syncing calendars and tasks.

### 3. OpenID Connect Callback (`pkg/modules/auth/openid/openid.go`)

The OIDC callback issues a fresh JWT token after validating the identity provider's response but does not check whether the Vikunja user account is disabled. If the user's identity provider session is still active, they receive a valid JWT despite being disabled in Vikunja.

## Impact

An administrator who disables a user account expects that user to be immediately locked out. In practice:

- **API tokens**: The user retains full API access for the remaining lifetime of any issued API tokens — potentially months or years.
- **CalDAV**: The user can continue reading and writing tasks/events via any CalDAV client.
- **OIDC**: The user can obtain a fresh, fully valid JWT by re-authenticating through their identity provider, completely bypassing the account disable.

## Proof of Concept

1. Create a user and generate an API token.
2. Disable the user account via the admin API or CLI.
3. Make an API request using the API token:
   ```bash
   curl -H "Authorization: Bearer tk_<token>" https://vikunja.example/api/v1/user
   ```
4. The request succeeds with a 200 response despite the account being disabled.

## References
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-94xm-jj8x-3cr4
- https://nvd.nist.gov/vuln/detail/CVE-2026-33668
- https://github.com/go-vikunja/vikunja/commit/033922309f492996c928122fb49b691339199c35
- https://github.com/go-vikunja/vikunja/commit/04704e0fde4b027039cf583110cee7afe136fc1b
- https://github.com/go-vikunja/vikunja/commit/0b04768d830c80e9fde1b0962db1499cc652da0e
- https://github.com/go-vikunja/vikunja/commit/fd452b9cb6457fd4f9936527a14c359818f1cca7
- https://github.com/go-vikunja/vikunja
- https://vikunja.io/changelog/vikunja-v2.2.2-was-released
