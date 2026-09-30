# [M] Arbitrary Command Injection due to Improper Command Sanitization

## Summary
Severity: Medium
Advisory: GHSA-hxwm-x553-x359
CWE: CWE-78
Ecosystem: npm
Published: 2021-08-05
Source: https://github.com/advisories/GHSA-hxwm-x553-x359
Type: github-advisory

## Affected
- npm: `@npmcli/git` — affected >=0 <2.0.8

## Details
### Summary
There exists a command injection vulnerability in `npmcli/git` versions <2.0.8 which may result in arbitrary shell command execution due to improper argument sanitization when `npmcli/git` is used to execute Git commands based on user controlled input. 

The impact of this issue is possible Arbitrary Command Injection when `npmcli/git` is run with untrusted (user controlled) Git command arguments. 

### Impact

Arbitrary Command Injection

### Details

`npmcli/git` prior to release `2.0.8` passed user controlled input as arguments to a shell command without properly sanitizing this input. Passing unsanitized input to a shell can lead to arbitrary command injection. For example passing `git+https://github.com/npm/git; echo hello world` would trigger the shell execution of `echo hello world`.  

This issue was remediated by no longer running `npmcli/git` git commands through an intermediate shell.

### Patches

This issue has been patched in release `2.0.8`

### Acknowledgements

This report was reported to us by @tyage (Ierae Security) through the [GitHub Bug Bounty Program](https://bounty.github.com).

## References
- https://github.com/npm/git/security/advisories/GHSA-hxwm-x553-x359
- https://github.com/npm/git/pull/29
