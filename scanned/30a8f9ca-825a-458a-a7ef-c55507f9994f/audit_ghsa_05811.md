# [C] conflibot vulnerable to command injection via crafted pull request branch names under pull_request_target

## Summary
Severity: Critical
Advisory: GHSA-2qvg-qr73-mqxp
CVE: CVE-2026-55158
CWE: CWE-78
Ecosystem: GitHub Actions
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-08-17
Source: https://github.com/advisories/GHSA-2qvg-qr73-mqxp
Type: github-advisory

## Affected
- GitHub Actions: `wktk/conflibot` — affected >=0 <1.2.1

## Details
### Impact

Versions of conflibot before `1.2.1` build `git` commands by string interpolation and run them through a shell. Several of the interpolated values are pull request branch names (`head.ref`), which are attacker-controlled: anyone can open a pull request (including from a fork) whose head branch name contains shell metacharacters such as `` ` ``, `$( )`, `;`, `|`, or `&`.

The recommended workflow runs conflibot on the `pull_request_target` event, where the job has access to the base repository's secrets and a write-scoped `GITHUB_TOKEN`. As a result, a crafted branch name causes arbitrary command execution on the runner with that write token in the environment, allowing an attacker to exfiltrate secrets and the token, push to the repository, or otherwise abuse the token's permissions. No special privileges and no maintainer interaction are required — the action runs automatically when the pull request is opened.

### Affected configurations

Any workflow using `wktk/conflibot` at a version earlier than `1.2.1`. The risk is highest under `pull_request_target` (the documented configuration), because that is where the write token and secrets are exposed to attacker-influenced refs.

### Patches

Fixed in `1.2.1` and `2.0.0`. All `git` invocations now use argument arrays via `execFile`/`spawn` instead of a shell, so branch names can no longer be interpreted as shell syntax, and pull requests are referenced by number through `refs/pull/<n>/head` rather than by branch name.

### Workarounds

There is no configuration-only workaround for affected versions. Upgrade to `wktk/conflibot@v2`. On GitHub-hosted runners this is a drop-in upgrade; self-hosted runners additionally need Node.js 24 support and git 2.38 or later.

### Resources

- Fix (v2.0.0): https://github.com/wktk/conflibot/commit/0107ac6
- Fix (v1.2.1): https://github.com/wktk/conflibot/commit/59e255c
- Releases: https://github.com/wktk/conflibot/releases/tag/v2.0.0 and https://github.com/wktk/conflibot/releases/tag/v1.2.1

## References
- https://github.com/wktk/conflibot/security/advisories/GHSA-2qvg-qr73-mqxp
- https://github.com/wktk/conflibot/commit/0107ac6
- https://github.com/wktk/conflibot/commit/59e255c
- https://github.com/wktk/conflibot
- https://github.com/wktk/conflibot/releases/tag/v1.2.1
- https://github.com/wktk/conflibot/releases/tag/v2.0.0
