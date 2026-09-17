# [M] Gitea: SSRF in restore-repo via unsanitized pull_request.yml Head.CloneURL

## Summary
Severity: Medium
Advisory: GHSA-xmj7-xj85-hfc3
CVE: CVE-2026-58441
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-xmj7-xj85-hfc3
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.27.0

## Details
### Summary
Gitea's `restore-repo` CLI command restores a repository from a dump
directory/archive. When parsing `pull_request.yml` from that dump, the
`Head.CloneURL` field is used to add a git remote and fetch from it with
no validation, because the safety check that's supposed to guard it
(`CheckAndEnsureSafePR`) is called with an empty `commonCloneBaseURL`,
which silently disables it. This lets a malicious dump make the Gitea
server execute `git fetch` against an attacker-chosen URL (SSRF), or
disclose a local git repository via `file://`. This is a different root
cause from the recently fixed path-traversal issue in the same command
(#38215), which patched `DownloadURL`/`PatchURL` but not `Head.CloneURL`.

### Details
`services/migrations/restore.go`'s `GetPullRequests()` unmarshals
`pull_request.yml` directly into `base.PullRequest` structs with no
validation of `Head.CloneURL`:

```go
err = yaml.Unmarshal(bs, &pulls)
...
for _, pr := range pulls {
    if pr.PatchURL != "" {
        pr.PatchURL = "file://" + util.FilePathJoinAbs(r.baseDir, pr.PatchURL)
    }
    CheckAndEnsureSafePR(pr, "", r)   // <-- empty baseURL
}
```

`CheckAndEnsureSafePR` (`services/migrations/common.go`) is supposed to
reject `Head.CloneURL`/`PatchURL` values that don't share a common base
URL:

```go
func hasBaseURL(toCheck, baseURL string) bool {
    if len(baseURL) > 0 && baseURL[len(baseURL)-1] != '/' {
        baseURL += "/"
    }
    return strings.HasPrefix(toCheck, baseURL)
}

func CheckAndEnsureSafePR(pr *base.PullRequest, commonCloneBaseURL string, g base.Downloader) bool {
    valid := true
    if pr.PatchURL != "" && !hasBaseURL(pr.PatchURL, commonCloneBaseURL) {
        pr.PatchURL = ""
        valid = false
    }
    if pr.Head.CloneURL != "" && !hasBaseURL(pr.Head.CloneURL, commonCloneBaseURL) {
        pr.Head.CloneURL = ""
        valid = false
    }
    return valid
}
```

`strings.HasPrefix(anything, "")` is always `true` in Go. Because
`restore.go` is the only caller that passes `""` as
`commonCloneBaseURL`, this check is a complete no-op on the restore-repo
path — `Head.CloneURL` survives unchanged regardless of its value. Every
other downloader (`github.go`, `gitlab.go`, `gitea_downloader.go`,
`codebase.go`, `codecommit.go`, `onedev.go`) passes a real base URL, so
they are not affected.

`services/migrations/gitea_uploader.go` then uses the unvalidated value
directly:

```go
err := g.gitRepo.AddRemote(remote, pr.Head.CloneURL, true)
// ... later: fetch from that remote
```

resulting in the server executing `git fetch` against an
attacker-controlled URL sourced from the dump file.

**RCE via git's `ext::` transport helper was tested and ruled out** — a
normal `git` install rejects it by default (`fatal: transport 'ext' not
allowed`), independent of Gitea's own configuration. This report is
scoped to SSRF and local git-repository disclosure.

Confirmed present, byte-for-byte identical, in `v1.26.4` (latest stable
tag), `release/v1.27`, and `main`, by direct checkout and diff.

### PoC
1. Create a dump directory following the normal `restore-repo` layout
   (`repo.yml`, etc.), and add a `pull_request.yml` containing at least
   one entry with:
```yaml
   - number: 1
     head:
       cloneURL: "http://<attacker-controlled-or-internal-host>:<port>/ssrf-proof"
       ref: "main"
```
2. Run `gitea restore-repo` against that dump directory for any repo
   owner.
3. Observe on the target host/listener: an actual `git` HTTP
   discovery request arrives, e.g.
   `GET /ssrf-proof/info/refs?service=git-upload-pack`, driven entirely
   by the value from the dump file.

Verified the core mechanism (steps 2–3, i.e. the unvalidated
`Head.CloneURL` surviving `CheckAndEnsureSafePR("")` and then being used
in a real `git remote add` + `git fetch`) with a minimal, standalone Go
program built from the **verbatim, unmodified** `hasBaseURL` /
`CheckAndEnsureSafePR` function bodies (attached: `gitea_ssrf_poc.go`),
run end-to-end against a local HTTP listener. The listener's access log
confirms the request actually arrives. 

### Impact
An attacker who can get an administrator to run `gitea restore-repo`
against a malicious dump (the same threat model already accepted for the
just-fixed path-traversal issue in this command, #38215) can make the
Gitea server issue a `git fetch` against an arbitrary attacker-chosen
URL. This allows:
- SSRF against internal-only services or cloud metadata endpoints
  reachable from the Gitea host.
- Disclosure of local git repositories reachable via `file://` paths
  readable by the Gitea process.

No public disclosure planned. Happy to provide further detail on
request.

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-xmj7-xj85-hfc3
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.27.0
