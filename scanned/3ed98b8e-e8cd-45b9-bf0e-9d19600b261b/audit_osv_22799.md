# [M] Improper Authentication in Arvados when using PAM as identity provider

## Summary
Severity: Medium
Advisory: CVE-2022-39238
Aliases: GHSA-87jr-xwhg-cxjv
CVSS: 4.2 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2022-09-23
Source: https://osv.dev/vulnerability/CVE-2022-39238
Type: osv

## Details
Arvados is an open source platform for managing and analyzing biomedical big data. In versions prior to 2.4.3, when using Portable Authentication Modules (PAM) for user authentication, if a user presented valid credentials but the account is disabled or otherwise not allowed to access the host (such as an expired password), it would still be accepted for access to Arvados. Other authentication methods (LDAP, OpenID Connect) supported by Arvados are not affected by this flaw. This issue is patched in version 2.4.3. Workaround for this issue is to migrate to a different authentication method supported by Arvados, such as LDAP.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39238.json
- https://github.com/arvados/arvados/security/advisories/GHSA-87jr-xwhg-cxjv
- https://nvd.nist.gov/vuln/detail/CVE-2022-39238
