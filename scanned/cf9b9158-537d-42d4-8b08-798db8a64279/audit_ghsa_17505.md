# [M] New authd users logging in via SSH are members of the root group

## Summary
Severity: Medium
Advisory: GHSA-g8qw-mgjx-rwjr
CVE: CVE-2025-5689
CWE: CWE-266, CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-06-16
Source: https://github.com/advisories/GHSA-g8qw-mgjx-rwjr
Type: github-advisory

## Affected
- Go: `github.com/ubuntu/authd` — affected >=0 <0.5.4

## Details
### Impact
When an authd user logs in via SSH for the first time (meaning they do not yet exist in the authd user database) and successfully authenticates via the configured broker, the user is considered a member of the root group in the context of that SSH session. This situation may allow the user to read and write files that are accessible by the root group, to which they should not have access. The user does not get root privileges or any capabilities beyond the access granted to the root group.

**Preconditions under which this vulnerability affects a system**
* authd was [installed via the PPA](https://documentation.ubuntu.com/authd/latest/howto/install-authd/#install-authd).
* An OAuth 2.0 application was registered in Microsoft Entra ID or Google IAM, and the respective authd broker was installed ([authd-msentraid](https://snapcraft.io/authd-msentraid) or [authd-google](https://snapcraft.io/authd-google)) and [configured](https://documentation.ubuntu.com/authd/latest/howto/configure-authd/#broker-configuration).
* sshd was [configured to enable SSH](https://documentation.ubuntu.com/authd/latest/howto/login-ssh/) access with authd, i.e.:
  ```
  UsePAM yes
  KbdInteractiveAuthentication yes
  ```
* The username is allowed by the `ssh_allowed_suffixes` option in the [broker configuriation](https://documentation.ubuntu.com/authd/latest/howto/login-ssh/#broker-configuration).
* The user is allowed by the [`allowed_users` option in the broker configuration](https://documentation.ubuntu.com/authd/latest/howto/configure-authd/#configure-allowed-users).
* The user successfully authenticates via the authd broker (Entra ID or Google IAM).
* The user did not log in locally before.

### Patches
Fixed by https://github.com/ubuntu/authd/commit/619ce8e55953b970f1765ddaad565081538151ab

### Workarounds
Configure the SSH server to not allow authenticating via authd, for example by setting `UsePAM no` or `KbdInteractiveAuthentication no` in the `sshd_config` (see https://documentation.ubuntu.com/authd/stable/howto/login-ssh/#ssh-configuration).

## References
- https://github.com/ubuntu/authd/security/advisories/GHSA-g8qw-mgjx-rwjr
- https://nvd.nist.gov/vuln/detail/CVE-2025-5689
- https://github.com/ubuntu/authd/commit/619ce8e55953b970f1765ddaad565081538151ab
- https://github.com/ubuntu/authd
