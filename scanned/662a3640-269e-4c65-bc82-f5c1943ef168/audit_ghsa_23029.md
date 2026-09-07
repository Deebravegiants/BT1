# [H] Apache ActiveMQ Artemis RCE Via Deserialization Gadget Chain

## Summary
Severity: High
Advisory: GHSA-r9vv-xj4w-g8m8
CVE: CVE-2016-4978
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-r9vv-xj4w-g8m8
Type: github-advisory

## Affected
- Maven: `org.apache.activemq:artemis-pom` — affected >=0 <1.4.0

## Details
The getObject method of the `javax.jms.ObjectMessage` class in the (1) JMS Core client, (2) Artemis broker, and (3) Artemis REST component in Apache ActiveMQ Artemis before 1.4.0 might allow remote authenticated users with permission to send messages to the Artemis broker to deserialize arbitrary objects and execute arbitrary code by leveraging gadget classes being present on the Artemis classpath.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-4978
- https://www.blackhat.com/docs/us-16/materials/us-16-Kaiser-Pwning-Your-Java-Messaging-With-Deserialization-Vulnerabilities.pdf
- https://web.archive.org/web/20210123172653/http://www.securityfocus.com/bid/93142
- https://lists.apache.org/thread.html/rc96ad63f148f784c84ea7f0a178c84a8985c6afccabbcd9847a82088@%3Ccommits.activemq.apache.org%3E
- https://lists.apache.org/thread.html/rc96ad63f148f784c84ea7f0a178c84a8985c6afccabbcd9847a82088%40%3Ccommits.activemq.apache.org%3E
- https://lists.apache.org/thread.html/rb2fd3bf2dce042e0ab3f3c94c4767c96bb2e7e6737624d63162df36d@%3Ccommits.activemq.apache.org%3E
- https://lists.apache.org/thread.html/rb2fd3bf2dce042e0ab3f3c94c4767c96bb2e7e6737624d63162df36d%40%3Ccommits.activemq.apache.org%3E
- https://lists.apache.org/thread.html/d4ffbc6a43a915324a394b2913ceb7d07bc352f2d08caa19df0aff02@%3Cissues.activemq.apache.org%3E
- https://lists.apache.org/thread.html/d4ffbc6a43a915324a394b2913ceb7d07bc352f2d08caa19df0aff02%40%3Cissues.activemq.apache.org%3E
- https://lists.apache.org/thread.html/7260bd0955c12aac5bd892039d3356ba3aa0ff4caaf2aa4fd4fe84a2@%3Cissues.activemq.apache.org%3E
- https://lists.apache.org/thread.html/7260bd0955c12aac5bd892039d3356ba3aa0ff4caaf2aa4fd4fe84a2%40%3Cissues.activemq.apache.org%3E
- https://github.com/apache/activemq-artemis
- https://access.redhat.com/errata/RHSA-2018:1451
- https://access.redhat.com/errata/RHSA-2018:1450
- https://access.redhat.com/errata/RHSA-2018:1449
- https://access.redhat.com/errata/RHSA-2018:1448
- https://access.redhat.com/errata/RHSA-2018:1447
- https://access.redhat.com/errata/RHSA-2017:3458
- https://access.redhat.com/errata/RHSA-2017:3456
- https://access.redhat.com/errata/RHSA-2017:3455
