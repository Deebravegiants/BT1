# [M] sudo-rs doesn't record authenticating user properly in timestamp

## Summary
Severity: Medium
Advisory: GHSA-q428-6v73-fc4q
CVE: CVE-2025-64517
CWE: CWE-287
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2025-11-13
Source: https://github.com/advisories/GHSA-q428-6v73-fc4q
Type: github-advisory

## Affected
- crates.io: `sudo-rs` — affected >=0.2.5 <0.2.10

## Details
### Summary
When `Defaults targetpw` (or `Defaults rootpw`) is enabled, the password of the target account (or root account) instead of the invoking user is used for authentication. `sudo-rs` prior to 0.2.10 incorrectly recorded the invoking user’s UID instead of the authenticated-as user's UID in the authentication timestamp. Any later `sudo` invocation on the same terminal while the timestamp was still valid would use that timestamp, potentially bypassing new authentication even if the policy would have required it.

### Impact
A highly-privileged user (able to run commands as other users, or as root, through sudo) who knows one password of an account they are allowed to run commands as, would be able to run commands as any other account the policy permits them to run commands for, even if they don't know the password for those accounts.

A common instance of this would be that a user can still use their own password to run commands as root (the default behaviour of `sudo`), effectively negating the intended behaviour of the `targetpw` or `rootpw` options.

### Example

With this in /etc/sudoers:
```
Defaults targetpw
user ALL=(ALL:ALL) ALL
```
First run:
```
user@machine$ sudo -g root whoami
[sudo: authenticate] Password: <password for user>
user
```
Then run:
```
user@machine$ sudo -u root whoami
root
```

### Affected versions

sudo-rs prior to 0.2.5 are not affected, since they do not offer `Defaults targetpw` or `Defaults rootpw`.

### Credits

This issue was discovered and reported by @Pingasmaster.

## References
- https://github.com/trifectatechfoundation/sudo-rs/security/advisories/GHSA-q428-6v73-fc4q
- https://nvd.nist.gov/vuln/detail/CVE-2025-64517
- https://github.com/trifectatechfoundation/sudo-rs/commit/8423fd986c3fa58b357f238c0db5e54baca5255d
- https://github.com/trifectatechfoundation/sudo-rs
- https://github.com/trifectatechfoundation/sudo-rs/releases/tag/v0.2.10
