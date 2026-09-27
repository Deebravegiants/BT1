# [M] Gitea: REST API exposes organization membership of private organizations to public

## Summary
Severity: Medium
Advisory: GHSA-jr5x-6h83-wrxf
CVE: CVE-2026-58417
CWE: CWE-200, CWE-863
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-jr5x-6h83-wrxf
Type: github-advisory

## Affected
- Go: `gitea.dev` — affected >=0 <1.27.0

## Details
### Summary

The endpoint  "/orgs/{org}/public_members/{username}" + GET exposes organization membership of public members in a private organization.

### PoC

1. Spin up the nightly container of Gitea.
2. Perform the default installation.
3. Register a new user (let's call this user "user1").
4. Create a new organization with "private" visibility. We will refer to this organization as "user1org".
5. Make the user "user1" inside the organization visible.
6. Log out and register a new user ("user2").
7. Create an access token for "user2" with full access to the API.
8. Use the endpoint "/orgs/{org}/public_members/{username}" + GET with the correct username of "user1", organization name, and access token of "user2" to query whether "user1" is a member of the organization. The following curl command demonstrates the usage:

curl -X 'GET' \
  'http://localhost:4700/api/v1/orgs/user1org/public_members/user1' \
  -H 'accept: application/json' \
  -H 'authorization: token <user2-token>'

9. You will receive status code 204, which leaks the organization membership.

### Impact

The vulnerability discloses organization membership. An information that is not accessible via the web app (the organization is hidden, and therefore, the organization membership on the user's profile page is also hidden).

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-jr5x-6h83-wrxf
- https://github.com/go-gitea/gitea/pull/38145
- https://github.com/go-gitea/gitea/commit/685b62c60fc595e3612a85f0895471876db56292
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.27.0
