# [C] Authentication cache in Active Directory Jenkins Plugin allows logging in with any password

## Summary
Severity: Critical
Advisory: GHSA-954f-xw44-56r2
CVE: CVE-2020-2301
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-954f-xw44-56r2
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:active-directory` — affected >=2.17 <2.20
- Maven: `org.jenkins-ci.plugins:active-directory` — affected >=0 <2.16.1

## Details
Jenkins Active Directory Plugin implements two separate modes: Integration with ADSI on Windows, and an OS agnostic LDAP-based mode. Optionally, to reduce lookup time, a cache can be configured to remember user lookups and user authentications.

In Active Directory Plugin prior to 2.20 and 2.16.1, when run in Windows/ADSI mode, the provided password was not used when looking up an applicable cache entry. This allows attackers to log in as any user using any password while a successful authentication of that user is still in the cache.

As a workaround for this issue, the cache can be disabled.

Active Directory Plugin 2.20 and 2.16.1 includes the provided password in cache entry lookup.

Additionally, the Java system property `hudson.plugins.active_directory.CacheUtil.noCacheAuth` can be set to `true` to no longer cache user authentications.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-2301
- https://github.com/jenkinsci/active-directory-plugin/commit/57e78ea7bb96b4e59405f28959ade2d26821163d
- https://github.com/CVEProject/cvelist/blob/381fe967666a5ce01625a7a050427aa4757e3ca6/2020/2xxx/CVE-2020-2301.json
- https://github.com/jenkinsci/active-directory-plugin
- https://www.jenkins.io/security/advisory/2020-11-04/#SECURITY-2123
