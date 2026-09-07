# [M] Use of a Key Past its Expiration Date and Insufficient Session Expiration in Maddy Mail Server

## Summary
Severity: Medium
Advisory: GHSA-6cp7-g972-w9m9
CVE: CVE-2022-24732
CWE: CWE-324, CWE-613
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2022-03-07
Source: https://github.com/advisories/GHSA-6cp7-g972-w9m9
Type: github-advisory

## Affected
- Go: `github.com/foxcpp/maddy` — affected >=0 <0.5.4

## Details
### Impact

Any configuration on any maddy version <0.5.4 using auth.pam is affected.

No password expiry or account expiry checking is done when authenticating using PAM.

### Patches

Patch is available as part of the 0.5.4 release.

### Workarounds

If /etc/shadow authentication is used, it is possible to replace auth.pam with auth.shadow which is not affected.

It is possible to blacklist expired accounts via existing filtering mechanisms (e.g. auth_map to invalid accounts in storage.imapsql).

### References

* https://github.com/foxcpp/maddy/blob/3412e59a2c92106e194fa69f2f1017c020037c9c/internal/auth/pam/pam.c
* https://linux.die.net/man/3/pam_acct_mgmt

### For more information
If you have any questions or comments about this advisory:
* Open an issue in https://github.com/foxcpp/maddy
* Email fox.cpp@disroot.org

## References
- https://github.com/foxcpp/maddy/security/advisories/GHSA-6cp7-g972-w9m9
- https://nvd.nist.gov/vuln/detail/CVE-2022-24732
- https://github.com/foxcpp/maddy/commit/7ee6a39c6a1939b376545f030a5efd6f90913583
- https://github.com/foxcpp/maddy
- https://github.com/foxcpp/maddy/releases/tag/v0.5.4
