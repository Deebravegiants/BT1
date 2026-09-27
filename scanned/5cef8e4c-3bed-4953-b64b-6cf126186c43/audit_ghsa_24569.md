# [H] Apache Geode unsafe deserialization of application objects

## Summary
Severity: High
Advisory: GHSA-95m2-p98f-24r5
CVE: CVE-2017-15693
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-95m2-p98f-24r5
Type: github-advisory

## Affected
- Maven: `org.apache.geode:geode-core` — affected >=1.0.0 <1.4.0

## Details
In Apache Geode before v1.4.0, the Geode server stores application objects in serialized form. Certain cluster operations and API invocations cause these objects to be deserialized. A user with DATA:WRITE access to the cluster may be able to cause remote code execution if certain classes are present on the classpath.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-15693
- https://github.com/apache/geode/pull/1166
- https://issues.apache.org/jira/browse/GEODE-3923
- https://lists.apache.org/thread.html/cc3ec1d06062f54fdaa0357874c1d148fc54bb955f2d2df4ca328a3d@%3Cuser.geode.apache.org%3E
