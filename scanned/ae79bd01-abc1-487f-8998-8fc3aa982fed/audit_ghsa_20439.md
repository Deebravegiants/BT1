# [H] Insecure Java Deserialization in Apache Karaf

## Summary
Severity: High
Advisory: GHSA-jh5g-9m4v-9vv9
CVE: CVE-2021-41766
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-01-28
Source: https://github.com/advisories/GHSA-jh5g-9m4v-9vv9
Type: github-advisory

## Affected
- Maven: `org.apache.karaf.management:org.apache.karaf.management.server` — affected >=0 <4.3.6

## Details
Apache Karaf allows monitoring of applications and the Java runtime by using the Java Management Extensions (JMX). JMX is a Java RMI based technology that relies on Java serialized objects for client server communication. Whereas the default JMX implementation is hardened against unauthenticated deserialization attacks, the implementation used by Apache Karaf is not protected against this kind of attack. The impact of Java deserialization vulnerabilities strongly depends on the classes that are available within the targets class path. Generally speaking, deserialization of untrusted data does always represent a high security risk and should be prevented. The risk is low as, by default, Karaf uses a limited set of classes in the JMX server class path. It depends of system scoped classes (e.g. jar in the lib folder).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-41766
- https://github.com/apache/karaf/pull/1475
- https://github.com/apache/karaf/commit/b42c82ca3b9a22bd92d249a1060a1953f4188bc2
- https://gitbox.apache.org/repos/asf?p=karaf.git;h=93a019c
- https://gitbox.apache.org/repos/asf?p=karaf.git;h=b42c82c
- https://github.com/apache/karaf
- https://issues.apache.org/jira/browse/KARAF-7312
- https://karaf.apache.org/security/cve-2021-41766.txt
