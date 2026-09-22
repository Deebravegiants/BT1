# [H] Apache NiFi JMS Deserialization issue

## Summary
Severity: High
Advisory: GHSA-p76j-5v6v-6c22
CVE: CVE-2018-1310
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-p76j-5v6v-6c22
Type: github-advisory

## Affected
- Maven: `org.apache.nifi:nifi` — affected >=0 <1.6.0

## Details
Apache NiFi JMS Deserialization issue because of ActiveMQ client vulnerability. Malicious JMS content could cause denial of service. See ActiveMQ CVE-2015-5254 announcement for more information. The fix to upgrade the activemq-client library to 5.15.3 was applied on the Apache NiFi 1.6.0 release. Users running a prior 1.x release should upgrade to the appropriate release.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1310
- https://nifi.apache.org/security.html#CVE-2018-1310
