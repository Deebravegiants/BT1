# [M] Gogs Vulnerable to Unauthenticated Organization Teams Information Disclosure via API

## Summary
Severity: Medium
Advisory: GHSA-744x-3838-5r56
CVE: CVE-2026-52815
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:N/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-744x-3838-5r56
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.14.3

## Details
## Summary

Gogs has an unauthenticated information disclosure vulnerability. The `GET /api/v1/orgs/:orgname/teams` endpoint at `internal/route/api/v1/org_team.go:8` returns all teams for any organization without requiring authentication. The route group at `internal/route/api/v1/api.go:380-385` lacks the `reqToken()` middleware, and the `listTeams()` handler performs no authentication check, exposing team IDs, names, descriptions, and permission levels to any unauthenticated caller.

## Affected Versions

Gogs (all current versions)

## Vulnerability Details

### Root Cause: Missing reqToken() middleware on org teams route group

`internal/route/api/v1/api.go` lines 380-385:

```go
// Org teams route group — no reqToken() middleware
m.Group("/:orgname", func() {
    m.Get("/teams", org.ListTeams) // No auth required
}, orgAssignment(true))
```

The `orgAssignment(true)` middleware only loads the organization object — it performs no authentication. The `listTeams()` handler at `org_team.go:8` returns all teams unconditionally:

```go
func ListTeams(c *context.APIContext) {
    org := c.Org.Organization
    teams, err := database.GetTeamsByOrgID(org.ID)
    // Returns all teams — no c.IsLogged check, no permission check
}
```

Compare with other org endpoints that correctly require authentication:

```go
m.Group("/orgs/:orgname", func() {
    // ... other endpoints ...
}, reqToken(), orgAssignment(true, true)) // reqToken() enforces auth
```

### Attack Chain

- Attacker sends `GET /api/v1/orgs/target-org/teams` with no authentication
- `orgAssignment(true)` loads the organization but does not check auth
- `ListTeams()` queries all teams and returns them
- Response includes team IDs, names, descriptions, and permission levels (read/write/admin/owner)

## Proof of Concept

```bash
# List all teams in an organization — no authentication needed
curl -s "http://TARGET:3000/api/v1/orgs/myorg/teams" | python3 -m json.tool

# Expected: 200 OK with full team list
# [
#   {
#     "id": 1,
#     "name": "Owners",
#     "description": "Admin team",
#     "permission": "owner"
#   },
#   {
#     "id": 2,
#     "name": "backend-devs",
#     "description": "Backend development team",
#     "permission": "write"
#   }
# ]
```

## Impact

An unauthenticated attacker can:

- Enumerate all teams within any organization, including private/internal teams
- Discover team permission levels (read/write/admin/owner), aiding privilege escalation planning
- Map organizational structure and identify high-value targets (admin/owner teams)
- Harvest team IDs for use in other API calls that may have weaker authorization checks

## Suggested Remediation

```go
m.Group("/:orgname", func() {
    m.Get("/teams", org.ListTeams)
}, reqToken(), orgAssignment(true))
```

Add `reqToken()` middleware to the org teams route group, consistent with other authenticated org endpoints. Additionally, `ListTeams()` should verify the authenticated user is a member of the organization.

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-744x-3838-5r56
- https://nvd.nist.gov/vuln/detail/CVE-2026-52815
- https://github.com/gogs/gogs/pull/8336
- https://github.com/gogs/gogs/commit/2ebc0e27069deade992219e10a89fbc44bec8bb9
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/releases/tag/v0.14.3
