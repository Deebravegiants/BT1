# [M] Gitea CVE-2026-20800 sibling endpoints not covered: revoked user still reads private repo objects via `/api/v1/user/starred` and private issue titles via `/api/v1/user/times`

## Summary
Severity: Medium
Advisory: GHSA-qf2f-qh6p-7v89
CVE: CVE-2026-59766
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-qf2f-qh6p-7v89
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.27.0

## Details
## Summary
CVE-2026-20800 fixed private-info leakage to revoked users only for the notification endpoint. Two
sibling endpoints that return data keyed on the caller's own relationship still do not re-check repo
access at output time:
- `GET /api/v1/user/starred` — `getStarredRepos()` computes a per-repo permission but still lists every
  starred repo (no filtering), so the full repo object (`full_name`, `private`, `clone_url`, `ssh_url`)
  of a now-inaccessible private repo is returned.
- `GET /api/v1/user/times` — `ListMyTrackedTimes()` queries by `UserID` only and `LoadAttributes` brings
  in the issue (`title`, `state`), leaking private issue titles after revocation.

## Steps to reproduce
Using the provided reproduction materials, as a revoked user:
1. Control: `GET /api/v1/repos/admin/starred-test` → **404**.
2. `GET /api/v1/user/starred` → leaks `admin/starred-test`, `private:true`, `clone_url`.
3. `GET /api/v1/user/times` → leaks `issue.title = "SECRET: …"`, `state`.

(Runtime-confirmed on `gitea/gitea:1.25.4`. Oracle = planted sentinel title; no real secret exfiltrated.)

## Impact
A former collaborator can enumerate private repos they starred and read private issue titles they logged
time on, indefinitely after access revocation. Metadata only (no repo content / comment bodies). Low.

## Suggested remediation
1. `getStarredRepos`: drop (or minimally redact) repos where `permission.HasAnyUnitAccessOrPublicAccess()`
   is false for the caller.
2. `ListMyTrackedTimes`: filter tracked-time entries by current repo access.
3. Optionally clear a user's stars / time entries for a private repo on revocation.

## Credit
Reported as part of an incomplete-patch measurement study (responsible disclosure).

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-qf2f-qh6p-7v89
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.27.0
