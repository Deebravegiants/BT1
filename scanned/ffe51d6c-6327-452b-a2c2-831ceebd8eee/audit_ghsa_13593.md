# [M] ZITADEL's password reset does not respect the "Ignoring unknown usernames" setting

## Summary
Severity: Medium
Advisory: GHSA-v683-rcxx-vpff
CVE: CVE-2023-44399
CWE: CWE-640
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-10-10
Source: https://github.com/advisories/GHSA-v683-rcxx-vpff
Type: github-advisory

## Affected
- Go: `github.com/zitadel/zitadel` — affected >=0 <2.37.3

## Details
### Impact
ZITADEL administrators can enable a setting called "Ignoring unknown usernames" which helps mitigate attacks that try to guess/enumerate usernames. While this settings was properly working during the authentication process it did not work correctly on the password reset flow. This meant that even if this feature was active that an attacker could use the password reset function to verify if an account exist within ZITADEL.

### Patches
This bug has been patched in versions >2.27.2 beginning with [2.37.3](https://github.com/zitadel/zitadel/releases/tag/v2.37.3) and [2.38.0](https://github.com/zitadel/zitadel/releases/tag/v2.38.0)

### Workarounds
None available we advise to updated if this is needed.

### References
None

## References
- https://github.com/zitadel/zitadel/security/advisories/GHSA-v683-rcxx-vpff
- https://nvd.nist.gov/vuln/detail/CVE-2023-44399
- https://github.com/zitadel/zitadel
- https://github.com/zitadel/zitadel/releases/tag/v2.37.3
- https://github.com/zitadel/zitadel/releases/tag/v2.38.0
