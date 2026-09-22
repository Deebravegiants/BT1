# [M] GitHub CLI can execute a git binary from the current directory

## Summary
Severity: Medium
Advisory: GHSA-fqfh-778m-2v32
Ecosystem: Go
Published: 2022-02-11
Source: https://github.com/advisories/GHSA-fqfh-778m-2v32
Type: github-advisory

## Affected
- Go: `github.com/cli/cli` — affected >=0 <1.2.1

## Details
### Impact
GitHub CLI depends on a `git.exe` executable being found in system `%PATH%` on Windows. However, if a malicious `.\git.exe` or `.\git.bat` is found in the current working directory at the time of running `gh`, the malicious command will be invoked instead of the system one.

Windows users who run `gh` inside untrusted directories are affected.

### Patches
Users should upgrade to GitHub CLI v1.2.1.

### Workarounds
Other than avoiding untrusted repositories, there is no workaround.

### References
https://github.com/golang/go/issues/38736

## References
- https://github.com/cli/cli/security/advisories/GHSA-fqfh-778m-2v32
