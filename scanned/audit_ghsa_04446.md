# [M] Gitea: Missing repository-unit authorization on issue-template API endpoints

## Summary
Severity: Medium
Advisory: GHSA-3fwp-p5rj-2pxf
CVE: CVE-2026-27783
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-3fwp-p5rj-2pxf
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.26.2

## Details
## Summary

Three Gitea API endpoints — `GET /repos/{owner}/{repo}/issue_templates`,
`GET /repos/{owner}/{repo}/issue_config` and `GET /repos/{owner}/{repo}/issue_config/validate`
— read files from the repository's **Code** default branch (`.gitea/ISSUE_TEMPLATE/*`
and `issue_config.yaml`) and return their contents, but are registered **without**
the `reqRepoReader(unit.TypeCode)` authorization middleware that every sibling
Code-tree endpoint in the same route group carries.

A user who has access to a private repository through *any single repository unit*
(for example an organization team granted only the **Issues** unit, with no Code
access) can therefore read the issue-template and issue-config files of that
repository's Code tree, which their permission set should not expose.

---

## Root cause

### The three endpoints lack the unit guard

`routers/api/v1/api.go:1433-1437`:

    m.Get("/issue_templates", context.ReferencesGitRepo(), repo.GetIssueTemplates)
    m.Get("/issue_config", context.ReferencesGitRepo(), repo.GetIssueConfig)
    m.Get("/issue_config/validate", context.ReferencesGitRepo(), repo.ValidateIssueConfig)
    m.Get("/languages", reqRepoReader(unit.TypeCode), repo.GetLanguages)
    m.Get("/licenses", reqRepoReader(unit.TypeCode), repo.GetLicenses)

`context.ReferencesGitRepo()` only opens the git repository — it performs no
permission check. Every other endpoint in this group that reads Code-tree content
is guarded with `reqRepoReader(unit.TypeCode)`: `/languages`, `/licenses`,
`/contents/*`, `/file-contents`, and `/{ball_type:tarball|zipball|bundle}/*`
(api.go:1418-1445). The three issue-template endpoints are the only Code-tree
readers in the group missing that guard.

The enclosing group runs `repoAssignment()` (api.go:1446), whose access check is
satisfied by `HasAnyUnitAccessOrPublicAccess` — i.e. access to **any** unit of the
repository is sufficient to pass. Without a per-unit `reqRepoReader`, the handlers
run for a caller who has no Code permission.

### The handlers return Code-tree file contents

`routers/api/v1/repo/repo.go`:

    func GetIssueTemplates(ctx *context.APIContext) {                       // :1179
        ret := issue.ParseTemplatesFromDefaultBranch(ctx.Repo.Repository, ctx.Repo.GitRepo)
        ...
        ctx.JSON(http.StatusOK, ret.IssueTemplates)
    }

    func GetIssueConfig(ctx *context.APIContext) {                          // :1209
        issueConfig, _ := issue.GetTemplateConfigFromDefaultBranch(ctx.Repo.Repository, ctx.Repo.GitRepo)
        ctx.JSON(http.StatusOK, issueConfig)
    }

`ParseTemplatesFromDefaultBranch` / `GetTemplateConfigFromDefaultBranch` read
`.gitea/ISSUE_TEMPLATE/*` and `issue_config.yaml` from the default (Code) branch
and return them in the JSON response.

---

## Proof of Concept

`victim-org/private-repo` is a private repository. The attacker is a member of an
organization team granted access to that repository through a non-Code unit only
(e.g. the Issues unit) — a supported Gitea permission configuration.

    GET /api/v1/repos/victim-org/private-repo/issue_templates HTTP/1.1
    Host: TARGET
    Authorization: token <attacker token>

The response is `200 OK` with the parsed contents of the repository's
`.gitea/ISSUE_TEMPLATE/*` files. The same applies to `/issue_config`. Because the
caller lacks the Code unit, every other Code-tree endpoint
(`/contents`, `/languages`, …) correctly returns `404`/`403` for the same token —
only these three return data.

---

## Impact

A repository collaborator whose granted permissions exclude the Code unit can read
the issue-template and issue-config files from the Code default branch of a private
repository. The exposure is limited to those specific configuration files (not
arbitrary Code-tree content), which is why this is rated low impact. It is
nonetheless a unit-level authorization bypass: the endpoints disclose Code-unit
content to callers the permission model is meant to exclude.

---

## Suggested fix

Add the same unit guard the sibling endpoints use, in `routers/api/v1/api.go`:

    m.Get("/issue_templates", reqRepoReader(unit.TypeCode), context.ReferencesGitRepo(), repo.GetIssueTemplates)
    m.Get("/issue_config", reqRepoReader(unit.TypeCode), context.ReferencesGitRepo(), repo.GetIssueConfig)
    m.Get("/issue_config/validate", reqRepoReader(unit.TypeCode), context.ReferencesGitRepo(), repo.ValidateIssueConfig)

(If issue templates are intended to be visible to Issues-unit users for issue
creation, `reqRepoReader(unit.TypeIssues)` is the appropriate guard — but the
current absence of any unit guard is the bug.)

---

## References

- CWE-862 Missing Authorization
- CWE-284 Improper Access Control
- OWASP A01:2021 Broken Access Control

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-3fwp-p5rj-2pxf
- https://github.com/go-gitea/gitea
