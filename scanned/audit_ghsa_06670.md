# [M] Gitea: Webhooks created by a collaborator keep firing after their repo access is revoked → ongoing real-time exfiltration of private repo content

## Summary
Severity: Medium
Advisory: GHSA-66m4-5jjr-2rg5
CVE: CVE-2026-58440
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-66m4-5jjr-2rg5
Type: github-advisory

## Affected
- Go: `gitea.dev` — affected >=0 <1.27.0

## Details
## Affected product
Gitea — `services/repository/collaboration.go` (`DeleteCollaboration`) + webhook delivery

## Summary
When a collaborator with admin permission on a private repo creates a webhook, that webhook keeps firing
after the collaborator's access is revoked. Gitea's revocation cleanup `DeleteCollaboration` removes the
collaboration record, recalculates accesses, drops watches, and unassigns issues — but it does **not**
remove or disable webhooks the user created, and webhook delivery never re-checks whether the creator still
has repo access. The former collaborator therefore receives the full payload (issue/comment bodies, commit
data) of all future repository events at their controlled endpoint, indefinitely and invisibly.

## Affected code
- `services/repository/collaboration.go` → `DeleteCollaboration()` — cleans watches/assignees only; no
  webhook cleanup.
- Webhook delivery path — fires on repo events without re-validating the creator's current access.

## Steps to reproduce
Using the provided reproduction materials:
1. Attacker (admin collaborator) creates a webhook → revoke access.
2. Control: `GET /api/v1/repos/admin/wh-repo` (attacker) → **404**.
3. `GET .../hooks` → webhook still `active=true`.
4. Admin creates a new issue **after** revocation → the catcher receives `action:"opened"`,
   `issue.title:"CRITICAL SECRET: …"`, `issue.body` (sentinel private key), `repository.private:true`.
(Runtime-confirmed on `gitea/gitea:1.25.4`. Catcher is an internal sentinel listener; the payload is a
planted sentinel, not real data; nothing is sent to any external/metadata endpoint.)

## Impact
Authenticated former admin-collaborator → ongoing real-time exfiltration of private content created after
revocation; invisible to the owner; scope crosses from the application boundary to data the user should no
longer access.

## Suggested remediation
1. On revocation, delete/disable webhooks created by the removed collaborator (or hand them to the owner).
2. Re-validate the creator's current repo access before each webhook delivery.
3. At minimum, warn admins on revocation if the user created webhooks.

## Credit
Reported as part of an incomplete-patch / authorization-residue measurement study (responsible disclosure).

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-66m4-5jjr-2rg5
- https://github.com/go-gitea/gitea/pull/38406
- https://github.com/go-gitea/gitea/pull/38426
- https://github.com/go-gitea/gitea/commit/de4b8277e9cb576f2315fb03b5ab6478b42a1d31
- https://github.com/go-gitea/gitea/commit/f69e15afe7496cc62e96dab244629c69eb31a7bf
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.27.0
