# [H] Gogs Vulnerable to CSRF Leading to Organization Owner Takeover

## Summary
Severity: High
Advisory: GHSA-pwx3-qcgw-vh7h
CVE: CVE-2026-52800
CWE: CWE-352
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-pwx3-qcgw-vh7h
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.14.3

## Details
## Summary

In **Gogs 0.14.1**, organization team member management can be performed via **GET requests without CSRF protection**.
If a victim who is an **organization owner** is logged in and is tricked into visiting a crafted link, an attacker-controlled user can be added to the **Owners** team. As a result, the attacker gains **organization owner–equivalent privileges**.

---

## Description

When a victim is logged in as an organization owner, **team member management endpoints are exposed via routes reachable by GET requests**, allowing state-changing operations without a CSRF token.

### Team action route allows GET

`internal/cmd/web.go:390`

```go
m.Route("/teams/:team/action/:action", "GET,POST", org.TeamsAction)
```

### CSRF validation is applied only to POST requests

Because the global CSRF check is limited to POST requests, state-changing operations reached via GET bypass CSRF protection entirely.

`internal/context/auth.go:56-61`

```go
if !options.SignOutRequired && !options.DisableCSRF &&
   c.Req.Method == "POST" && !isAPIPath(c.Req.URL.Path) {
    csrf.Validate(c.Context, c.csrf)
    if c.Written() {
        return
    }
}
```

### TeamsAction performs state changes regardless of HTTP method

`TeamsAction` does not branch on the HTTP method. Instead, it performs state-changing operations (such as adding or removing members) based solely on query parameters (`uid`, `uname`) and the `:action` path parameter.
Since the route explicitly allows GET, the `add` action can be executed via GET.

`internal/route/org/teams.go:38-83`

```go
func TeamsAction(c *context.Context) {
    uid := com.StrTo(c.Query("uid")).MustInt64()
    if uid == 0 {
        c.Redirect(c.Org.OrgLink + "/teams")
        return
    }

    page := c.Query("page")
    var err error
    switch c.Params(":action") {
    case "add":
        if !c.Org.IsOwner {
            c.NotFound()
            return
        }
        uname := c.Query("uname")
        var u *database.User
        u, err = database.Handle.Users().GetByUsername(c.Req.Context(), uname)
        // ...
        err = c.Org.Team.AddMember(u.ID)
        page = "team"
    }
}
```

### Adding a user to the Owners team grants organization owner privileges

When a user joins the **Owners** team, `OrgUser.IsOwner` is set to `true`. Therefore, adding a user to the Owners team directly results in granting organization owner–equivalent privileges.

`internal/database/org_team.go:566-576`

```go
ou := new(OrgUser)
if _, err = sess.Where("uid = ?", userID).
    And("org_id = ?", orgID).Get(ou); err != nil {
    return err
}
ou.NumTeams++
if t.IsOwnerTeam() {
    ou.IsOwner = true
}
if _, err = sess.ID(ou.ID).AllCols().Update(ou); err != nil {
    return err
}
```

### Related issue: organization member actions are also state-changing via GET

For reference, organization member management endpoints are also exposed as GET routes that perform state changes without CSRF protection.

`internal/cmd/web.go:382`

```go
m.Get("/members/action/:action", org.MembersAction)
```

`MembersAction` similarly does not branch on HTTP method and performs state-changing operations (public/private toggle, remove, leave) based on query parameters and the `:action` path parameter.

`internal/route/org/members.go:31-71`

```go
func MembersAction(c *context.Context) {
    uid := com.StrTo(c.Query("uid")).MustInt64()
    if uid == 0 {
        c.Redirect(c.Org.OrgLink + "/members")
        return
    }

    org := c.Org.Organization
    var err error
    switch c.Params(":action") {
    case "private":
        err = database.ChangeOrgUserStatus(org.ID, uid, false)
    case "public":
        err = database.ChangeOrgUserStatus(org.ID, uid, true)
    case "remove":
        err = org.RemoveMember(uid)
    case "leave":
        err = org.RemoveMember(c.User.ID)
    }
}
```

---

## Steps to Reproduce

1. Prepare a target user account to be added (e.g., `attacker`).

2. Confirm that the victim user is an **owner** of the target organization (e.g., `org3`) and is logged in.

3. Cause the victim’s browser to perform a **top-level navigation** to the following URL:

   ```
   http://localhost:10880/org/org3/teams/owners/action/add?uid=1&uname=attacker
   ```
<img width="2019" height="322" alt="image" src="https://github.com/user-attachments/assets/342a627a-04e8-47bd-818a-9c2b05a75446" />


4. After the request completes, verify that the `attacker` user can access:

   ```
   http://localhost:10880/org/org3/settings
   ```

   confirming that organization owner privileges have been obtained.

<img width="2010" height="285" alt="image" src="https://github.com/user-attachments/assets/03945bb1-e9c5-4e42-ad3a-9f6d63b7d86d" />


<img width="2016" height="893" alt="image" src="https://github.com/user-attachments/assets/55d7db13-52cf-471b-a6d3-aa4186c8b547" />




---

## Impact

Successful exploitation allows an attacker to obtain **organization owner privileges**, resulting in:

* Full control over organization repositories, settings, and members
* Unauthorized access to private repositories (confidentiality impact)
* Modification or deletion of repositories and settings (integrity impact)
* Repository deletion or disruption leading to service unavailability (availability impact)

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-pwx3-qcgw-vh7h
- https://nvd.nist.gov/vuln/detail/CVE-2026-52800
- https://github.com/gogs/gogs/pull/8321
- https://github.com/gogs/gogs/commit/070df61ecd14c75b0aca93090f860b87ab17ac19
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/releases/tag/v0.14.3
