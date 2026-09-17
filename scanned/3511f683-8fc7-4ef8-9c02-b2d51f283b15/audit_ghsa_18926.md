# [C] Apache Druid’s Kerberos authenticator uses a weak fallback secret

## Summary
Severity: Critical
Advisory: GHSA-w88f-4875-99c8
CVE: CVE-2025-59390
CWE: CWE-338
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-11-26
Source: https://github.com/advisories/GHSA-w88f-4875-99c8
Type: github-advisory

## Affected
- Maven: `org.apache.druid:druid` — affected >=0 <35.0.0

## Details
Apache Druid’s Kerberos authenticator uses a weak fallback secret when the `druid.auth.authenticator.kerberos.cookieSignatureSecret` configuration is not explicitly set. In this case, the secret is generated using `ThreadLocalRandom`, which is not a crypto-graphically secure random number generator. This  may allow an attacker to predict or brute force the secret used to sign authentication cookies, potentially enabling token forgery or authentication bypass. Additionally, each process generates its own fallback secret, resulting in inconsistent secrets across nodes. This causes authentication failures in distributed or multi-broker deployments, effectively leading to a incorrectly configured clusters. Users are advised to configure a strong `druid.auth.authenticator.kerberos.cookieSignatureSecret`

This issue affects Apache Druid: through 34.0.0.

Users are recommended to upgrade to version 35.0.0, which fixes the issue making it mandatory to set `druid.auth.authenticator.kerberos.cookieSignatureSecret` when using the Kerberos authenticator. Services will fail to come up if the secret is not set.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-59390
- https://github.com/apache/druid/pull/18368
- https://github.com/apache/druid
- https://lists.apache.org/thread/jwjltllnntgj1sb9wzsjmvwm9f8rlhg8
- http://www.openwall.com/lists/oss-security/2025/11/26/1
