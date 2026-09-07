# [H] Apache Ivy External Entity Reference vulnerability

## Summary
Severity: High
Advisory: GHSA-2jc4-r94c-rp7h
CVE: CVE-2022-46751
CWE: CWE-611, CWE-91
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:L (CVSS_V3)
Published: 2023-08-21
Source: https://github.com/advisories/GHSA-2jc4-r94c-rp7h
Type: github-advisory

## Affected
- Maven: `org.apache.ivy:ivy` — affected >=0 <2.5.2

## Details
Improper Restriction of XML External Entity Reference, XML Injection (aka Blind XPath Injection) vulnerability in Apache Software Foundation Apache Ivy.This issue affects any version of Apache Ivy prior to 2.5.2.

When Apache Ivy prior to 2.5.2 parses XML files - either its own configuration, Ivy files or Apache Maven POMs - it will allow downloading external document type definitions and expand any entity references contained therein when used.

This can be used to exfiltrate data, access resources only the machine running Ivy has access to or disturb the execution of Ivy in different ways.

Starting with Ivy 2.5.2 DTD processing is disabled by default except when parsing Maven POMs where the default is to allow DTD processing but only to include a DTD snippet shipping with Ivy that is needed to deal with existing Maven POMs that are not valid XML files but are nevertheless accepted by Maven. Access can be be made more lenient via newly introduced system properties where needed.

Users of Ivy prior to version 2.5.2 can use Java system properties to restrict processing of external DTDs, see the section about "JAXP Properties for External Access restrictions" inside Oracle's "Java API for XML Processing (JAXP) Security Guide".

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-46751
- https://github.com/apache/ant-ivy/commit/2be17bc18b0e1d4123007d579e43ba1a4b6fab3d
- https://docs.oracle.com/en/java/javase/13/security/java-api-xml-processing-jaxp-security-guide.html#GUID-94ABC0EE-9DC8-44F0-84AD-47ADD5340477
- https://gitbox.apache.org/repos/asf?p=ant-ivy.git;a=commit;h=2be17bc18b0e1d4123007d579e43ba1a4b6fab3d
- https://github.com/apache/ant-ivy
- https://lists.apache.org/thread/1dj60hg5nr36kjr4p1100dwjrqookps8
- https://lists.apache.org/thread/9gcz4xrsn8c7o9gb377xfzvkb8jltffr
- http://www.openwall.com/lists/oss-security/2023/09/06/9
