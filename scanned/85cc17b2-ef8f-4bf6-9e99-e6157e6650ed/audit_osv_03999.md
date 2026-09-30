# [H] Apache ActiveMQ, Apache ActiveMQ Broker, Apache ActiveMQ All: Authenticated user can perform RCE via DestinationView MBean exposed by Jolokia

## Summary
Severity: High
Advisory: BIT-activemq-2026-41044
Aliases: CVE-2026-41044, GHSA-mr6m-xj7v-3cv3
Ecosystem: Bitnami
Published: 2026-04-28
Source: https://osv.dev/vulnerability/BIT-activemq-2026-41044
Type: osv

## Affected
- Bitnami: `activemq` — affected >=6.0.0 <6.2.5

## Details
Improper Input Validation, Improper Control of Generation of Code ('Code Injection') vulnerability in Apache ActiveMQ, Apache ActiveMQ Broker, Apache ActiveMQ All.

An authenticated attacker can use the admin web console page to construct a malicious broker name that bypasses name validation to include an xbean binding that can be later used by a VM transport to load a remote Spring XML application.
The attacker can then use the DestinationView mbean to send a message to trigger a VM transport creation that will reference this malicious broker name which can lead to loading the malicious Spring XML context file.


Because Spring's ResourceXmlApplicationContext instantiates all singleton beans before the BrokerService validates the configuration, arbitrary code execution occurs on the broker's JVM through bean factory methods such as Runtime.exec().

This issue affects Apache ActiveMQ: before 5.19.6, from 6.0.0 before 6.2.5; Apache ActiveMQ Broker: before 5.19.6, from 6.0.0 before 6.2.5; Apache ActiveMQ All: before 5.19.6, from 6.0.0 before 6.2.5.

Users are recommended to upgrade to version 6.2.5 or 5.19.6, which fixes the issue.

## References
- http://www.openwall.com/lists/oss-security/2026/04/23/6
- https://activemq.apache.org/security-advisories.data/CVE-2026-41044-announcement.txt
- https://nvd.nist.gov/vuln/detail/CVE-2026-41044
- https://access.redhat.com/security/cve/CVE-2026-41044
- https://bugzilla.redhat.com/show_bug.cgi?id=2461409
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-41044.json
