# [H] File Browser’s insecure JWT handling can lead to session replay attacks after logout

## Summary
Severity: High
Advisory: GHSA-7xwp-2cpp-p8r7
CVE: CVE-2025-53826
CWE: CWE-305, CWE-384, CWE-613
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-07-16
Source: https://github.com/advisories/GHSA-7xwp-2cpp-p8r7
Type: github-advisory

## Affected
- Go: `github.com/filebrowser/filebrowser` — affected >=0
- Go: `github.com/filebrowser/filebrowser/v2` — affected >=0

## Details
### Summary

File Browser’s authentication system issues long-lived JWT tokens that remain valid even after the user logs out. Please refer to the CWE's listed in this report for further reference and system standards. In summary, the main issue is:

- Tokens remain valid after logout (session replay attacks)

In this report, I used docker as the documentation instruct:

```
docker run \
    -v filebrowser_data:/srv \
    -v filebrowser_database:/database \
    -v filebrowser_config:/config \
    -p 8080:80 \
    filebrowser/filebrowser
```

### Details

**Issue: Tokens remain valid after logout (session replay attacks)**

After logging in and receiving a JWT token, the user can explicitly "log out." However, this action does not invalidate the issued JWT. Any captured token can be replayed post-logout until it expires naturally. The backend does not track active sessions or invalidate existing tokens on logout. Login request:

```
POST /api/login HTTP/1.1
Host: machine.local:8090
Content-Length: 69

{"username":"admin","password":"password-here","recaptcha":""}
```

The check found in the code `https://github.com/filebrowser/filebrowser/blob/master/http/auth.go` is not enough. There is no server-side blacklist or token invalidation on logout. Token renewal and validity only depends on expiry and user store timestamps:

```
expired := !tk.VerifyExpiresAt(time.Now().Add(time.Hour), true)
updated := tk.IssuedAt != nil && tk.IssuedAt.Unix() < d.store.Users.LastUpdate(tk.User.ID)
```

### PoC

**Issue: Tokens remain valid after logout (session replay attacks)**

- Login and capture the generate JWT. Eg. the http request:

```
POST /api/login HTTP/1.1
Host: machine.local:8090
Content-Length: 69

{"username":"admin","password":"password-here","recaptcha":""}
```

- Logout in the dashboard. And then try to use the old generated JWT to access any authenticated endpoint eg:

```
GET /api/resources HTTP/1.1
Host: machine.local:8090
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36
X-Auth: Old-JWT-token-here
Content-Length: 173
Accept: */*
Referer: http://machine.local:8090/files/
Accept-Encoding: gzip, deflate, br
Accept-Language: en-US,en;q=0.9
Content-Length: 26

Connection: keep-alive
```

### Impact

- A valid JWT remains active after user logout.
- If stolen, tokens persist access indefinitely until expiry.
- Violates OWASP Top 10 A2:2021 - Broken Authentication.

### Recommendations

- Read all CWE's attached in this report
- Invalidate JWTs on logout via session store / token blacklist.
- Reduce JWT ExpiresAt where possible or use short-lived + refresh tokens.

## References
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-7xwp-2cpp-p8r7
- https://nvd.nist.gov/vuln/detail/CVE-2025-53826
- https://github.com/filebrowser/filebrowser/issues/5216
- https://github.com/filebrowser/filebrowser
