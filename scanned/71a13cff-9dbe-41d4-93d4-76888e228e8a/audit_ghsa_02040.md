# [H] Apache ActiveMQ Artemis vulnerable to Improper Access Control

## Summary
Severity: High
Advisory: GHSA-q7fr-vqhq-v5xr
CVE: CVE-2021-26118
CWE: CWE-284, CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2021-06-16
Source: https://github.com/advisories/GHSA-q7fr-vqhq-v5xr
Type: github-advisory

## Affected
- Maven: `org.apache.activemq:artemis-openwire-protocol` — affected >=0 <2.16.0

## Details
While investigating ARTEMIS-2964 it was found that the creation of advisory messages in the OpenWire protocol head of Apache ActiveMQ Artemis 2.15.0 bypassed policy based access control for the entire session. Production of advisory messages was not subject to access control in error.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-26118
- https://github.com/apache/activemq-artemis/commit/e5566d52116d81611d914548adc3cbb14d7118d4
- https://github.com/apache/activemq-artemis
- https://lists.apache.org/thread.html/rafd5d7cf303772a0118865262946586921a65ebd98fc24f56c812574%40%3Cannounce.apache.org%3E
- https://lists.apache.org/thread.html/rafd5d7cf303772a0118865262946586921a65ebd98fc24f56c812574@%3Cannounce.apache.org%3E
- https://mail-archives.apache.org/mod_mbox/activemq-users/202101.mbox/%3CCAH%2BvQmMUNnkiXv2-d3ucdErWOsdnLi6CgnK%2BVfixyJvTgTuYig%40mail.gmail.com%3E
- https://security.netapp.com/advisory/ntap-20210827-0002
