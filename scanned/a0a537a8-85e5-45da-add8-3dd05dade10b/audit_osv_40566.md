# [H] Apache Hive: Unauthenticated authentication bypass in HiveServer2 HTTP SAML bearer-token validation allows impersonation of any Hive user

## Summary
Severity: High
Advisory: CVE-2026-53561
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-53561
Type: osv

## Details
An improper authentication vulnerability in HiveServer2 SAML bearer-token validation in Apache Hive 4.0.0 through 4.2.0 (and later unreleased branches) on deployments using HTTP transport with hive.server2.authentication=SAML allows an unauthenticated network attacker to authenticate as an arbitrary Hive user and obtain an authenticated HiveServer2 session via a forged Authorization: Bearer token sent to the /cliservice HTTP endpoint. Users are recommended to upgrade to 4.2.1 version that includes the fix for this issue.

Access / authorization required: No Hive credentials, SAML IdP login, or knowledge of the server signing secret is required. The attacker only needs network reachability to the HiveServer2 HTTP port (typically /cliservice), directly or through a reverse proxy such as Apache Knox that forwards unauthenticated requests to HS2. The instance must have SAML authentication enabled in HTTP mode. Deployments where Knox handles SSO and HiveServer2 uses LDAP/Kerberos (not native SAML mode) are not affected by this specific issue.

## References
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53561.json
- https://lists.apache.org/thread/6d56mk501fp4f8cb5wvrpj2jwd9knt05
- https://nvd.nist.gov/vuln/detail/CVE-2026-53561
- https://issues.apache.org/jira/browse/HIVE-29653
- https://github.com/apache/hive/commit/6ca06ca1104ff7462363087a867d70d546134774
- https://github.com/apache/hive
