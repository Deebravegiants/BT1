# [C] Ibexa User Bundle is missing password change validation

## Summary
Severity: Critical
Advisory: GHSA-x93p-w2ch-fg67
CVE: CVE-2025-67719
CWE: CWE-620
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-12-10
Source: https://github.com/advisories/GHSA-x93p-w2ch-fg67
Type: github-advisory

## Affected
- Packagist: `ibexa/user` — affected >=5.0.0-beta1 <5.0.4

## Details
### Impact
The vulnerability is in the password change dialog in the back office. During the transition from v4 to v5 a mistake was made in the validation code which caused the validation of the previous password to not run as expected. This made it possible for a logged in user to change password in the back office without knowing the previous password. For example if someone logs in, leaves their workstation unlocked, and another person uses the same machine.

### Credit
The issue was reported to us by Code-Rhapsodie. We thank them for their responsible disclosure!
https://www.code-rhapsodie.fr/

### Patches
- See "Patched versions".
- https://github.com/ibexa/user/commit/9d485bf385e6401c9f7ee80287d8ccd00f73dcf4

### Workarounds
None.

## References
- https://github.com/ibexa/user/security/advisories/GHSA-x93p-w2ch-fg67
- https://nvd.nist.gov/vuln/detail/CVE-2025-67719
- https://github.com/ibexa/user/commit/9d485bf385e6401c9f7ee80287d8ccd00f73dcf4
- https://developers.ibexa.co/security-advisories/ibexa-sa-2025-005-password-change-and-xss-vulnerabilities-in-back-office
- https://github.com/ibexa/user
