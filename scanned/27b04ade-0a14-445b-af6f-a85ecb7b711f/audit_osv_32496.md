# [H] Zitadel Expired JWT Keys Usable for Authorization Grants

## Summary
Severity: High
Advisory: CVE-2025-31123
Aliases: GHSA-h3q7-347g-qwhf
CVSS: 8.7 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:N)
Published: 2025-03-31
Source: https://osv.dev/vulnerability/CVE-2025-31123
Type: osv

## Details
Zitadel is open-source identity infrastructure software. A vulnerability existed where expired keys can be used to retrieve tokens. Specifically, ZITADEL fails to properly check the expiration date of the JWT key when used for Authorization Grants. This allows an attacker with an expired key to obtain valid access tokens. This vulnerability does not affect the use of JWT Profile for OAuth 2.0 Client Authentication on the Token and Introspection endpoints, which correctly reject expired keys. This vulnerability is fixed in 2.71.6, 2.70.8, 2.69.9, 2.68.9, 2.67.13, 2.66.16, 2.65.7, 2.64.6, and 2.63.9.

## References
- https://github.com/zitadel/zitadel/releases/tag/v2.63.9
- https://github.com/zitadel/zitadel/releases/tag/v2.64.6
- https://github.com/zitadel/zitadel/releases/tag/v2.65.7
- https://github.com/zitadel/zitadel/releases/tag/v2.66.16
- https://github.com/zitadel/zitadel/releases/tag/v2.67.13
- https://github.com/zitadel/zitadel/releases/tag/v2.68.9
- https://github.com/zitadel/zitadel/releases/tag/v2.69.9
- https://github.com/zitadel/zitadel/releases/tag/v2.70.8
- https://github.com/zitadel/zitadel/releases/tag/v2.71.6
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/31xxx/CVE-2025-31123.json
- https://github.com/zitadel/zitadel/security/advisories/GHSA-h3q7-347g-qwhf
- https://nvd.nist.gov/vuln/detail/CVE-2025-31123
- https://github.com/zitadel/zitadel/commit/315503beabd679f2e6aec0c004f0f9d2f5b53ed3
