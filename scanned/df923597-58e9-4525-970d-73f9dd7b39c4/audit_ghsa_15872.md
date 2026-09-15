# [M] Jenkins Credentials plugin reveals encrypted values of credentials to users with Extended Read permission

## Summary
Severity: Medium
Advisory: GHSA-62jv-j4w7-5hh8
CVE: CVE-2024-47805
CWE: CWE-200, CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-10-02
Source: https://github.com/advisories/GHSA-62jv-j4w7-5hh8
Type: github-advisory

## Affected
- Maven: `org.jenkins-ci.plugins:credentials` — affected >=1372 <1381.v2c3a
- Maven: `org.jenkins-ci.plugins:credentials` — affected >=0 <1371.1373.v4eb

## Details
Jenkins Credentials Plugin 1380.va_435002fa_924 and earlier, except 1371.1373.v4eb_fa_b_7161e9, does not redact encrypted values of credentials using the `SecretBytes` type (e.g., Certificate credentials, or Secret file credentials from Plain Credentials Plugin) when accessing item `config.xml` via REST API or CLI.

This allows attackers with Item/Extended Read permission to view encrypted `SecretBytes` values in credentials.

This issue is similar to SECURITY-266 in the 2016-05-11 security advisory, which applied to the `Secret` type used for inline secrets and some credentials types.

Credentials Plugin 1381.v2c3a_12074da_b_ redacts the encrypted values of credentials using the `SecretBytes` type in item `config.xml` files.

This fix is only effective on Jenkins 2.479 and newer, LTS 2.462.3 and newer. While Credentials Plugin 1381.v2c3a_12074da_b_ can be installed on Jenkins 2.463 through 2.478 (both inclusive), encrypted values of credentials using the `SecretBytes` type will not be redacted when accessing item `config.xml` via REST API or CLI.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-47805
- https://www.jenkins.io/security/advisory/2024-10-02/#SECURITY-3373
