# [C] Apache Kafka does not validate JWT tokens in its OAUTHBEARER authentication implementation

## Summary
Severity: Critical
Advisory: GHSA-28jg-cgg7-j4wc
CVE: CVE-2026-33557
CWE: CWE-1285
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-04-20
Source: https://github.com/advisories/GHSA-28jg-cgg7-j4wc
Type: github-advisory

## Affected
- Maven: `org.apache.kafka:kafka-clients` — affected >=4.1.0 <4.1.2

## Details
A security vulnerability has been identified in Apache Kafka. By default, the broker property `sasl.oauthbearer.jwt.validator.class` is set to `org.apache.kafka.common.security.oauthbearer.DefaultJwtValidator`. It accepts any JWT token without validating its signature, issuer, or audience. An attacker can generate a JWT token from any issuer with the `preferred_username` set to any user, and the broker will accept it.

Apache advises Kafka users using kafka v4.1.0 or v4.1.1 to set the config `sasl.oauthbearer.jwt.validator.class` to `org.apache.kafka.common.security.oauthbearer.BrokerJwtValidator` explicitly to avoid this vulnerability. Since Kafka v4.1.2 and v4.2.0 and later, the issue is fixed and will correctly validate the JWT token.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-33557
- https://github.com/apache/kafka/commit/01d8e7db8d08dbd538892b409457ea6bfcc2a422
- https://github.com/apache/kafka
- https://kafka.apache.org/cve-list
- https://lists.apache.org/thread/v57o00hm6yszdpdnvqx2ss4561yh953h
- http://www.openwall.com/lists/oss-security/2026/04/17/2
