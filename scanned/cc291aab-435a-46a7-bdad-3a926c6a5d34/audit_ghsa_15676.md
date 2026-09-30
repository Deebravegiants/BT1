# [M] ZITADEL Vulnerable to Session Information Leakage

## Summary
Severity: Medium
Advisory: GHSA-cvw9-c57h-3397
CVE: CVE-2024-39683
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-07-05
Source: https://github.com/advisories/GHSA-cvw9-c57h-3397
Type: github-advisory

## Affected
- Go: `github.com/zitadel/zitadel` — affected >=2.0.0 <2.53.8
- Go: `github.com/zitadel/zitadel` — affected >=2.54.0 <2.54.5
- Go: `github.com/zitadel/zitadel` — affected >=2.55.0 <2.55.1

## Details
### Impact

ZITADEL provides users the ability to list all user sessions of the current user agent (browser) by API and in the Console UI.

Due to a missing check, user sessions without that information (e.g. when created though the session service) were incorrectly listed exposing potentially other user's sessions.

Note that the Login UI was never affected and there was no possibility to take over such a session.

### Patches

2.x versions are fixed on >= [2.55.1](https://github.com/zitadel/zitadel/releases/tag/v2.55.1)
2.54.x versions are fixed on >= [2.54.5](https://github.com/zitadel/zitadel/releases/tag/v2.54.5)
2.53.x versions are fixed on >= [2.53.8](https://github.com/zitadel/zitadel/releases/tag/v2.53.8)

ZITADEL recommends upgrading to the latest versions available in due course.

### Workarounds

There is no workaround since a patch is already available.

### References

- https://github.com/zitadel/zitadel/pull/8231
- https://discord.com/channels/927474939156643850/1254096852937347153
- https://github.com/zitadel/zitadel/issues/8213

### Questions
If you have any questions or comments about this advisory, please email us at [security@zitadel.com](mailto:security@zitadel.com)

### Credits
Thanks to @cybertransformer, @Avolicious, @AmirhoseinBrz and @srividyaj for finding and reporting the vulnerability.

## References
- https://github.com/zitadel/zitadel/security/advisories/GHSA-cvw9-c57h-3397
- https://nvd.nist.gov/vuln/detail/CVE-2024-39683
- https://github.com/zitadel/zitadel/issues/8213
- https://github.com/zitadel/zitadel/pull/8231
- https://github.com/zitadel/zitadel/commit/4a262e42abac2208b02fefaf68ba1a5121649f04
- https://github.com/zitadel/zitadel/commit/c2093ce01507ca8fc811609ff5d391693360c3da
- https://github.com/zitadel/zitadel/commit/d04f208486a418a45b884b9ca8433e5ad9790d73
- https://discord.com/channels/927474939156643850/1254096852937347153
- https://github.com/zitadel/zitadel
- https://github.com/zitadel/zitadel/releases/tag/v2.53.8
- https://github.com/zitadel/zitadel/releases/tag/v2.54.5
- https://github.com/zitadel/zitadel/releases/tag/v2.55.1
