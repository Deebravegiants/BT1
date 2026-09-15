# [H] ZITADEL is vulnerable to Account Takeover with deactivated Instance IdP

## Summary
Severity: High
Advisory: GHSA-j4g7-v4m4-77px
CVE: CVE-2025-64717
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-11-14
Source: https://github.com/advisories/GHSA-j4g7-v4m4-77px
Type: github-advisory

## Affected
- Go: `github.com/zitadel/zitadel` — affected >=4.0.0-rc.1 <4.6.6
- Go: `github.com/zitadel/zitadel` — affected >=3.0.0-rc.1 <3.4.4
- Go: `github.com/zitadel/zitadel` — affected >=2.50.0 <2.71.19
- Go: `github.com/zitadel/zitadel` — affected >=1.80.0-v2.20.0.20240403060621-5b3946b67ef6 <1.80.0-v2.20.0.20251112124840-33c51deb2040

## Details
### Summary

A vulnerability in ZITADEL's federation process allowed auto-linking users from external identity providers to existing users in ZITADEL even if the corresponding IdP was not active or if the organization did not allow federated authentication.

### Impact

This vulnerability stems from the platform's failure to correctly check or enforce an organization's specific security settings during the authentication flow. An Organization Administrator can explicitly disable an IdP or disallow federation, but this setting was not being honored during the auto-linking process.

This allowed an unauthenticated attacker to initiate a login using an IdP that should have been disabled for that organization. The platform would incorrectly validate the login and, based on a matching criteria, link the attacker's external identity to an existing internal user account.

This may result in a full Account Takeover, bypassing the organization's mandated security controls. Note that accounts with MFA enabled can not be taken over by this attack. Also note that only IdPs create on an instance level would allow this to work. IdPs registered on another organization would always be denied in the (auto-)linking process.

### Affected Versions

Systems running one of the following versions are affected:
- **v4.x**: `4.0.0-rc.1` through `4.6.5`
- **v3.x**: `3.0.0-rc.1` through `3.4.3`
- **v2.x**: `2.50.0` through `2.71.18`

### Patches

The vulnerability has been addressed in the latest release. The patch resolves the issue by correctly validating the organization's login policy before auto-linking an external user.

- v4.x: Upgrade to version [4.6.6](https://github.com/zitadel/zitadel/releases/tag/v4.6.6) or later.
- v3.x: Update to version [3.4.4](https://github.com/zitadel/zitadel/releases/tag/v3.4.4) or later.
- v2.x: Update to version [2.71.19](https://github.com/zitadel/zitadel/releases/tag/v2.71.19) or later.

### Workarounds

Upgrading to a patched version is the recommended solution.

### Questions

If you have any questions or comments about this advisory, please email Zitadel at [security@zitadel.com](mailto:security@zitadel.com)

### Credits

Thanks to Jan Kühnlein - kultify for finding and reporting the vulnerability.

## References
- https://github.com/zitadel/zitadel/security/advisories/GHSA-j4g7-v4m4-77px
- https://nvd.nist.gov/vuln/detail/CVE-2025-64717
- https://github.com/zitadel/zitadel/commit/33c51deb20402dd5720e32cfb0c1d5fdc752f2e0
- https://github.com/zitadel/zitadel
- https://github.com/zitadel/zitadel/releases/tag/v2.71.19
- https://github.com/zitadel/zitadel/releases/tag/v3.4.4
- https://github.com/zitadel/zitadel/releases/tag/v4.6.6
