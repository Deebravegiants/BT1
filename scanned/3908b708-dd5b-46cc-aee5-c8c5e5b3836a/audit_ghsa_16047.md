# [H] Artifact poisoning vulnerability in action-download-artifact v5 and earlier

## Summary
Severity: High
Advisory: GHSA-5xr6-xhww-33m4
CWE: CWE-349
Ecosystem: GitHub Actions
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2024-11-25
Source: https://github.com/advisories/GHSA-5xr6-xhww-33m4
Type: github-advisory

## Affected
- GitHub Actions: `dawidd6/action-download-artifact` — affected >=0 <6

## Details
### Summary

In versions of `dawidd6/action-download-artifact` before v6, a repository's forks were also searched by default when attempting to find matching artifacts. This could be exploited by an unprivileged attacker to introduce compromised artifacts (such as malicious executables) into a privileged workflow context, as creating a fork requires no privileges.

Users should immediately upgrade to v6 or newer, which changes the default behavior to avoid searching forks for matching artifacts. Users who cannot upgrade should explicitly set `allow_forks: false` to disable searching forks for artifacts.

### Details

GitHub's artifact storage for workflows does not natively distinguish between artifacts created by a repository and artifacts created by forks of that repository. As a result, attempting to retrieve the "latest" artifact for a workflow run can return artifacts produced by a fork, rather than its upstream. 

Because any GitHub user can create a fork of a public repository, this allows for artifact poisoning in the following scenarios (as well as potentially others):

1. Repository `alice/foo` runs `build.yml`, producing `build.exe`
2. Repository `alice/foo` runs `publish.yml`, which uses `action-download-artifact@v5` to retrieve the latest `build.exe` from `build.yml`

To compromise `publish.yml` in this scenario, Mallory forks `alice/foo` to `mallory/foo`, and then modifies `build.yml` to produce a compromised `build.exe`. Mallory can then repeatedly trigger their copy of `build.yml` to ensure that their compromised `build.exe` is always the latest artifact, meaning that Alice's `publish.yml` will retrieve it.

Additional details on this vulnerability can be found in this blog post from 2022:

* https://www.legitsecurity.com/blog/artifact-poisoning-vulnerability-discovered-in-rust

### Impact

This vulnerability impacts all repositories on GitHub that use `action-download-artifacts@v5` or older and do **not** disable `allow_forks: true`, which is the default.

If a repository is affected, the severity ranges from downstream contamination (such as publishing attacker-controlled artifacts) to direct workflow compromise (if the retrieved artifact is then executed in a privileged workflow context, such as `push` or `pull_request_target`).

## References
- https://github.com/dawidd6/action-download-artifact/security/advisories/GHSA-5xr6-xhww-33m4
- https://github.com/dawidd6/action-download-artifact/commit/bf251b5aa9c2f7eeb574a96ee720e24f801b7c11
- https://github.com/dawidd6/action-download-artifact
- https://www.legitsecurity.com/blog/artifact-poisoning-vulnerability-discovered-in-rust
