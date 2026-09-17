# [M] SFTPGo has insufficient access control for password reset

## Summary
Severity: Medium
Advisory: GHSA-hw5f-6wvv-xcrh
CVE: CVE-2024-37897
CWE: CWE-287, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-06-20
Source: https://github.com/advisories/GHSA-hw5f-6wvv-xcrh
Type: github-advisory

## Affected
- Go: `github.com/drakkan/sftpgo/v2` — affected >=2.2.0 <2.6.1

## Details
### Impact

SFTPGo WebAdmin and WebClient support password reset. This feature is disabled in the default configuration.
In SFTPGo versions prior to v2.6.1, if the feature is enabled, even users with access restrictions (e.g. expired) can reset their password and log in.

### Patches

Fixed in v2.6.1.

### Workarounds

The following workarounds are available:

- keep the password reset feature disabled.
- Set a blank email address for users and admins with access restrictions so they cannot receive the email with the reset code and exploit the vulnerability.

## References
- https://github.com/drakkan/sftpgo/security/advisories/GHSA-hw5f-6wvv-xcrh
- https://nvd.nist.gov/vuln/detail/CVE-2024-37897
- https://github.com/drakkan/sftpgo/commit/1f8ac8bfe16100b0484d6c91e1e8361687324423
- https://github.com/drakkan/sftpgo/commit/3462bba3f41cbc75486474991b9e3ac1b5f1e583
- https://github.com/drakkan/sftpgo
- https://github.com/drakkan/sftpgo/releases/tag/v2.6.1
