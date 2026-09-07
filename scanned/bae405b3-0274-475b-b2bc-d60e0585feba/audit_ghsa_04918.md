# [H] Gitea: Authorization Bypass via "Allow edits from maintainers" allows unauthorized commits to any readable repo

## Summary
Severity: High
Advisory: GHSA-mm7c-rhg6-qr4r
CVE: CVE-2026-26231
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2026-06-16
Source: https://github.com/advisories/GHSA-mm7c-rhg6-qr4r
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.26.2

## Details
## Summary

Any authenticated low-privilege user with read access to a repository can push arbitrary commits directly to that repository, bypassing all write-access checks.

## Vulnerability

Gitea's "Allow edits from maintainers" PR option can be abused via reverse-fork PRs:

1. The web UI PR-create endpoint binds `allow_maintainer_edit=true` **without** verifying that the submitter has write access to the HEAD repository.
2. Gitea allows creating a PR where **BASE = attacker's fork** and **HEAD = upstream target**. The attacker is "maintainer" of the BASE (their own fork), so the flag is set against the upstream HEAD.
3. On `git push` over HTTP/SSH, Gitea relaxes the required access mode to `Read` when `SupportProcReceive` is enabled ([`routers/web/repo/githttp.go`](https://github.com/go-gitea/gitea/blob/v1.25.5/routers/web/repo/githttp.go#L189), [`routers/private/serv.go`](https://github.com/go-gitea/gitea/blob/v1.25.5/routers/private/serv.go#L337)) and defers enforcement to the pre-receive hook.
4. The pre-receive hook calls [`CanMaintainerWriteToBranch`](https://github.com/go-gitea/gitea/blob/v1.25.5/models/issues/pull_list.go#L72) (`models/issues/pull_list.go`), which finds the malicious PR, sees `AllowMaintainerEdit=true`, and checks whether the pusher has write access to the **BASE** repo. Since BASE is the attacker's own fork, the check passes and the push is authorized against the upstream.

## Exploitation

1. Attacker forks the target repository.
2. Attacker visits the web compare endpoint and creates a PR with `BASE = their_fork`, `HEAD = upstream`, and "Allow edits from maintainers" checked.
3. Attacker clones their fork, makes a commit, and runs `git push <upstream_url> <branch>` — the push is accepted.

## Reproduction

```bash
python3 poc.py --repo http://gitea:3000/victim/repo --user attacker --password attacker_pass
```
[poc.py](https://github.com/user-attachments/files/26641541/poc.py)

Expected output:
```
[+] target: victim/my_repo  default branch: main
[*] forking -> attacker/my_repo_pocfork (202)
[+] fork ready
[+] malicious PR created (BASE=attacker fork, HEAD=upstream)

remote: . Processing 1 references
remote: Processed 1 references in total
To http://192.168.101.20:3000/victim/my_repo.git
   e5c07b3..9a0b884  main -> main

[+] latest commit on victim/my_repo@main: 'PoC: unauthorized commit via maintainer-edit bypass'
[+] CONFIRMED: unauthorized push to upstream succeeded.
```

A `PWNED.txt` file will appear on the target repo's default branch, committed by the attacker who has no write access.


## Impact

Full repository compromise. Any logged-in user can backdoor any repository they can read, including all public repositories on the instance.

## Suggested Fix

Two independent checks are missing; both should be added for defense in depth:

1. **At PR creation:** before setting `AllowMaintainerEdit = true`, verify the submitter has write access to the **HEAD** repository.
2. **In `CanMaintainerWriteToBranch`:** verify that the PR's HEAD repo matches the repository being pushed to, and that the PR was opened by a legitimate owner/writer of the HEAD repository. Do not trust `AllowMaintainerEdit` solely based on BASE write access.

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-mm7c-rhg6-qr4r
- https://github.com/go-gitea/gitea
