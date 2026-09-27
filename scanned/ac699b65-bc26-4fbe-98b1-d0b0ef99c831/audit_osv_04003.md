# [H] Apache ActiveMQ Broker, Apache ActiveMQ, Apache ActiveMQ All: LdapNetworkConnector instantiates denied transports and a remote-properties broker

## Summary
Severity: High
Advisory: BIT-activemq-2026-49434
Aliases: CVE-2026-49434
Ecosystem: Bitnami
Published: 2026-07-06
Source: https://osv.dev/vulnerability/BIT-activemq-2026-49434
Type: osv

## Affected
- Bitnami: `activemq` — affected >=6.0.0 <6.2.7

## Details
Improper Input Validation vulnerability in Apache ActiveMQ Broker, Apache ActiveMQ, Apache ActiveMQ All.

An attacker that has access to publish or modify entries in LDAP that match the configured searchBase and searchFilter can instantiate denied transports inside the broker JVM. This can be used to fetch an attacker URL and spawn a second BrokerService inside the same JVM.
This issue affects Apache ActiveMQ Broker: before 5.19.8, from 6.0.0 before 6.2.7; Apache ActiveMQ: before 5.19.8, from 6.0.0 before 6.2.7; Apache ActiveMQ All: before 5.19.8, from 6.0.0 before 6.2.7.


Users are recommended to upgrade to version 6.2.7 or 5.19.8, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/06/29/8
- https://lists.apache.org/thread/hcjh7kdk4l85tb9ksmvcnkhso1ngj50o
- https://nvd.nist.gov/vuln/detail/CVE-2026-49434
