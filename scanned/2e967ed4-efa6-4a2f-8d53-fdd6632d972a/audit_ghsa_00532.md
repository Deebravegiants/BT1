# [C] Code execution via deserialization in org.apache.ignite:ignite-core

## Summary
Severity: Critical
Advisory: GHSA-qcjv-wfcg-mmpr
CVE: CVE-2018-8018
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-16
Source: https://github.com/advisories/GHSA-qcjv-wfcg-mmpr
Type: github-advisory

## Affected
- Maven: `org.apache.ignite:ignite-core` — affected >=0 <2.6

## Details
Apache Ignite 2.5 and earlier serialization mechanism does not have a list of classes allowed for serialization/deserialization, which makes it possible to run arbitrary code when 3-rd party vulnerable classes are present in Ignite classpath. The vulnerability can be exploited if the one sends a specially prepared form of a serialized object to GridClientJdkMarshaller deserialization endpoint.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8018
- https://github.com/apache/ignite/commit/82a7b8209fcf56971d12cb10410a38ed632215b
- https://access.redhat.com/errata/RHSA-2018:3768
- https://github.com/advisories/GHSA-qcjv-wfcg-mmpr
- https://issues.apache.org/jira/browse/IGNITE-8565
- https://lists.apache.org/thread.html/e0fdf53114a321142ecfa5cfa17658090f0b4e1677de431e329b37ab@%3Cdev.ignite.apache.org%3E
