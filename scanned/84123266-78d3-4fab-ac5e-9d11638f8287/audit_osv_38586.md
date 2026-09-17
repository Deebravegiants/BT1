# [H] Apache Camel: Camel-Infinispan: Unsafe Deserialization in Remote Aggregation Repository

## Summary
Severity: High
Advisory: CVE-2026-40858
Aliases: GHSA-4xwx-hvv7-7prj
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-27
Source: https://osv.dev/vulnerability/CVE-2026-40858
Type: osv

## Details
The camel-infinispan component's ProtoStream-based remote aggregation repository deserializes data read from a remote Infinispan cache using java.io.ObjectInputStream without applying any ObjectInputFilter. An attacker who can write to the Infinispan cache used by a Camel application can inject a crafted serialized Java object that, when read during normal aggregation repository operations such as get or recover, results in arbitrary code execution in the context of the application.

This issue affects Apache Camel: from 4.0.0 before 4.14.7, from 4.15.0 before 4.18.2, from 4.19.0 before 4.20.0.

Users are recommended to upgrade to version 4.20.0, which fixes the issue. If users are on the 4.14.x LTS releases stream, then they are suggested to upgrade to 4.14.7. If users are on the 4.18.x releases stream, then they are suggested to upgrade to 4.18.2.

The JIRA ticket:  https://issues.apache.org/jira/browse/CAMEL-23322  refers to the various commits that resolved the issue, and have more details. This issue follows the same class of vulnerability previously addressed in CVE-2024-22369, CVE-2024-23114 and CVE-2026-25747.

## References
- https://repo.maven.apache.org/maven2
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-40858.json
- https://access.redhat.com/errata/RHSA-2026:17668
- https://access.redhat.com/errata/RHSA-2026:22453
- https://access.redhat.com/security/cve/CVE-2026-40858
- https://camel.apache.org/security/CVE-2026-40858.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40858.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-40858
- https://bugzilla.redhat.com/show_bug.cgi?id=2463179
