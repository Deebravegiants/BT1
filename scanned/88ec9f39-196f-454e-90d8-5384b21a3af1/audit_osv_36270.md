# [M] AliasVault is Missing Origin Validation in Android Passkey Credential Provider

## Summary
Severity: Medium
Advisory: CVE-2026-22694
Aliases: GHSA-mvg4-wvjv-332q
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:N)
Published: 2026-01-14
Source: https://osv.dev/vulnerability/CVE-2026-22694
Type: osv

## Details
AliasVault is a privacy-first password manager with built-in email aliasing. AliasVault Android versions 0.24.0 through 0.25.2 contained an issue in how passkey requests from Android apps were validated. Under certain local conditions, a malicious app could attempt to obtain a passkey response for a site it was not authorized to access. The issue involved incomplete validation of calling app identity, origin, and RP ID in the Android credential provider. This issue was fixed in AliasVault Android 0.25.3.

## References
- https://github.com/aliasvault/aliasvault/releases/tag/0.25.3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/22xxx/CVE-2026-22694.json
- https://github.com/aliasvault/aliasvault/security/advisories/GHSA-mvg4-wvjv-332q
- https://nvd.nist.gov/vuln/detail/CVE-2026-22694
- https://github.com/aliasvault/aliasvault/issues/1440
- https://github.com/aliasvault/aliasvault/commit/b3350473103d6138ab2b63ca130c211717eac67d
- https://github.com/aliasvault/aliasvault/pull/1441
