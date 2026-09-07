# [M] Gitea: OIDC userinfo Endpoint Returns Identity Claims Without Enforcing API Token Scopes

## Summary
Severity: Medium
Advisory: GHSA-mg4f-x9v4-6h2p
CVE: CVE-2026-55982
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-mg4f-x9v4-6h2p
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.27.0

## Details
### Summary

The OIDC userinfo endpoint (`GET /login/oauth/userinfo`) accepts Gitea API tokens as bearer credentials but does not enforce API token scopes before returning identity claims.

A personal access token scoped only to `read:misc` can successfully retrieve user information from the OIDC userinfo endpoint, even though the same token is denied access to user-related REST API endpoints that enforce scope checks.

As a result, identity information remains accessible through the OIDC endpoint regardless of the scopes assigned to the API token.

### Details

Gitea supports scoped personal access tokens and enforces scope checks on user-related REST API endpoints.

For example, a token scoped only to `read:misc` is denied access to endpoints such as:

| Endpoint | Required Scope |
|----------|----------------|
| `GET /api/v1/user` | `read:user` |
| `GET /api/v1/user/emails` | `read:user` |
| `GET /api/v1/user/orgs` | `read:organization` |

Requests to these endpoints return:

```http
403 Forbidden
```

with a scope-related error.

However, the same `read:misc` token can be supplied as a bearer credential to:

```http
GET /login/oauth/userinfo
Authorization: Bearer <token>
```

and receives a successful response containing identity claims.

Observed claims include:

- `email`
- `groups`

The `groups` claim contains organization and team membership information associated with the authenticated user.

This behavior indicates that the OIDC userinfo endpoint accepts API tokens but does not apply scope restrictions before returning identity claims.

### PoC

#### PoC Details

Proof-of-concept code: 
https://anonymous.4open.science/r/Gitea_PoC-EC93/3_poc_oidc_userinfo_scope_bypass

#### Reproduction Steps

1. Create a personal access token with only the following scope:

```text
read:misc
```

2. Verify that the token cannot access user-related REST API endpoints:

```http
GET /api/v1/user
GET /api/v1/user/emails
GET /api/v1/user/orgs
```

Each request returns:

```http
403 Forbidden
```

3. Send the same token to the OIDC userinfo endpoint:

```http
GET /login/oauth/userinfo
Authorization: Bearer <read-misc-token>
```

4. Observe that the request succeeds and returns identity claims, for example:

```json
{
  "email": "user@example.com",
  "groups": [
    ...
  ]
}
```

### Impact

Holders of narrowly scoped API tokens can obtain identity information through the OIDC userinfo endpoint regardless of the scopes assigned to the token.

The issue does not provide access to repositories, issues, pull requests, administrative functionality, or data belonging to other users.

Impact is limited to disclosure of identity information associated with the authenticated user. However, it weakens the authorization boundary established by API token scopes because identity claims remain accessible even when the token lacks user- or organization-related scopes.

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-mg4f-x9v4-6h2p
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.27.0
