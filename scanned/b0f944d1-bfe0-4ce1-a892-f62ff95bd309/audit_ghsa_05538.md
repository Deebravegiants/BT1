# [M] Zitadel has a user enumeration vulnerability in Login UIs

## Summary
Severity: Medium
Advisory: GHSA-pvm5-9frx-264r
CVE: CVE-2026-23511
CWE: CWE-203, CWE-204
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-01-15
Source: https://github.com/advisories/GHSA-pvm5-9frx-264r
Type: github-advisory

## Affected
- Go: `github.com/zitadel/zitadel` — affected >=4.0.0 <4.9.1
- Go: `github.com/zitadel/zitadel` — affected >=0 <3.4.6

## Details
### Summary

A user enumeration vulnerability has been discovered in Zitadel's login interfaces. An unauthenticated attacker can exploit this flaw to confirm the existence of valid user accounts by iterating through usernames and userIDs.

### Impact

The login UIs (in version 1 and 2) provide the possibility to request a password reset, where an email will be sent to the user with a link to a verification endpoint.
By submitting arbitrary userIDs to these endpoints, an attacker can differentiate between valid and invalid accounts based on the system's response.

For an effective exploit the attacker needs to iterate through the potential set of userIDs. The impact can be limited by implementing [rate limiting](https://zitadel.com/docs/self-hosting/manage/production#limits-and-quotas) or similar measures to limit enumeration of userIDs.

Additionally, Zitadel includes a security feature "Ignoring unknown usernames", designed to prevent username enumeration attacks by presenting a generic response for both valid and invalid usernames on the login page. The login UI V2 did not handle the setting correctly and would allow attackers to enumerate through usernames to check their existence.

### Affected Versions

All versions within the following ranges, including release candidates (RCs), are affected:
- **v4.x**: `4.0.0` through `4.9.0`
- **3.x**: `3.0.0` through `3.4.5`
- **2.x**: `2.0.0` through `2.71.19`

### Patches

The vulnerability has been addressed in the latest releases. The patch resolves the issue by returning a generic error message, which does not indicate it the user exists.

4.x: Upgrade to >=[4.9.1](https://github.com/zitadel/zitadel/releases/tag/v4.9.1)
3.x: Update to >=[3.4.6](https://github.com/zitadel/zitadel/releases/tag/v3.4.6)
2.x: Update to >=[3.4.6](https://github.com/zitadel/zitadel/releases/tag/v3.4.6)

### Workarounds

The recommended solution is to update ZITADEL to a patched version. You can limit the impact by implementing [rate limiting](https://zitadel.com/docs/self-hosting/manage/production#limits-and-quotas) or similar measures to limit enumeration of userIDs.

There is no workaround for the "Ignoring unknown usernames" issue in login V2. Please upgrade to a patched version, if you rely on this feature.

### Questions

If you have any questions or comments about this advisory, please email us at [security@zitadel.com](mailto:security@zitadel.com)

### Credits

Thanks to Niklas Kunz from Seamly for reporting this vulnerability from their pentest.

## References
- https://github.com/zitadel/zitadel/security/advisories/GHSA-pvm5-9frx-264r
- https://nvd.nist.gov/vuln/detail/CVE-2026-23511
- https://github.com/zitadel/zitadel/commit/0bb00dd9fc4e5e965f8e14fa2161a5076f3c308d
- https://github.com/zitadel/zitadel/commit/b85ab69e4679b0268e2b0e9b4cd04e934af10dd2
- https://github.com/zitadel/zitadel/commit/c300d4cc6a2775ab17ddfe76492f24170f8b858d
- https://github.com/zitadel/zitadel
- https://github.com/zitadel/zitadel/releases/tag/v3.4.6
- https://github.com/zitadel/zitadel/releases/tag/v4.9.1
