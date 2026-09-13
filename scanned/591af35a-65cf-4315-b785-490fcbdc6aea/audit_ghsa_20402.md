# [M] Improper Privilege Management in shelljs

## Summary
Severity: Medium
Advisory: GHSA-64g7-mvw6-v9qj
CWE: CWE-269
Ecosystem: npm
Published: 2022-01-14
Source: https://github.com/advisories/GHSA-64g7-mvw6-v9qj
Type: github-advisory

## Affected
- npm: `shelljs` — affected >=0 <0.8.5

## Details
### Impact
Output from the synchronous version of `shell.exec()` may be visible to other users on the same system. You may be affected if you execute `shell.exec()` in multi-user Mac, Linux, or WSL environments, or if you execute `shell.exec()` as the root user.

Other shelljs functions (including the asynchronous version of `shell.exec()`) are not impacted.

### Patches
Patched in shelljs 0.8.5

### Workarounds
Recommended action is to upgrade to 0.8.5.

### References
https://huntr.dev/bounties/50996581-c08e-4eed-a90e-c0bac082679c/

### For more information
If you have any questions or comments about this advisory:
* Ask at https://github.com/shelljs/shelljs/issues/1058
* Open an issue at https://github.com/shelljs/shelljs/issues/new

## References
- https://github.com/shelljs/shelljs/security/advisories/GHSA-64g7-mvw6-v9qj
- https://github.com/shelljs/shelljs
- https://huntr.dev/bounties/50996581-c08e-4eed-a90e-c0bac082679c
