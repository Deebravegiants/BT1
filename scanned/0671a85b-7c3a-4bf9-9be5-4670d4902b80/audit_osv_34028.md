# [C] ZITADEL has broken authN and authZ in session API and resulting session tokens

## Summary
Severity: Critical
Advisory: CVE-2025-53895
Aliases: GHSA-6c5p-6www-pcmr
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-07-15
Source: https://osv.dev/vulnerability/CVE-2025-53895
Type: osv

## Details
ZITADEL is an open source identity management system. Starting in version 2.53.0 and prior to versions 4.0.0-rc.2, 3.3.2, 2.71.13, and 2.70.14, vulnerability in ZITADEL's session management API allows any authenticated user to update a session if they know its ID, due to a missing permission check. This flaw enables session hijacking, allowing an attacker to impersonate another user and access sensitive resources. Versions prior to `2.53.0` are not affected, as they required the session token for updates. Versions 4.0.0-rc.2, 3.3.2, 2.71.13, and 2.70.14 fix the issue.

## References
- https://github.com/zitadel/zitadel/releases/tag/v2.70.14
- https://github.com/zitadel/zitadel/releases/tag/v2.71.13
- https://github.com/zitadel/zitadel/releases/tag/v3.3.2
- https://github.com/zitadel/zitadel/releases/tag/v4.0.0-rc.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/53xxx/CVE-2025-53895.json
- https://github.com/zitadel/zitadel/security/advisories/GHSA-6c5p-6www-pcmr
- https://nvd.nist.gov/vuln/detail/CVE-2025-53895
