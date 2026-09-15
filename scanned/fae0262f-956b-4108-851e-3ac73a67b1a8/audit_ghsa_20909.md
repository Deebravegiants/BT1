# [H] SFTPGo vulnerable to recovery codes abuse

## Summary
Severity: High
Advisory: GHSA-54qx-8p8w-xhg8
CVE: CVE-2022-36071
CWE: CWE-287, CWE-916
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-54qx-8p8w-xhg8
Type: github-advisory

## Affected
- Go: `github.com/drakkan/sftpgo/v2` — affected >=2.2.0 <2.3.4

## Details
### Impact

SFTPGo WebAdmin and WebClient support login using TOTP (Time-based One Time Passwords) as a seconday authentication factor. Because TOTPs are often configured on mobile devices that can be lost, stolen or damaged, SFTPGo also supports recovery codes. These are a set of one time use codes that can be used instead of the TOTP.

In SFTPGo versions from v2.2.0 to v2.3.3 recovery codes can be generated before enabling two-factor authentication.
An attacker who knows the user's password could potentially generate some recovery codes and then bypass two-factor authentication after it is enabled on the account at a later time.

### Patches

Fixed in v2.3.4.
Recovery codes can now only be generated after enabling two-factor authentication and are deleted after disabling it.

### Workarounds

Regenerate recovery codes after enabling two-factor authentication.

### References

https://github.com/drakkan/sftpgo/issues/965

## References
- https://github.com/drakkan/sftpgo/security/advisories/GHSA-54qx-8p8w-xhg8
- https://nvd.nist.gov/vuln/detail/CVE-2022-36071
- https://github.com/drakkan/sftpgo/issues/965
- https://github.com/drakkan/sftpgo
