# [M] Cross-site Scripting in Eclipse Mojarra

## Summary
Severity: Medium
Advisory: GHSA-rjhx-c9qh-qh8f
CVE: CVE-2019-17091
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-rjhx-c9qh-qh8f
Type: github-advisory

## Affected
- Maven: `org.glassfish:javax.faces` — affected >=0 <2.2.20
- Maven: `org.glassfish:jakarta.faces` — affected >=0 <2.3.10

## Details
faces/context/PartialViewContextImpl.java in Eclipse Mojarra, as used in Mojarra for Eclipse EE4J before 2.3.10 and Mojarra JavaServer Faces, allows Reflected XSS because a client window field is mishandled.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-17091
- https://github.com/eclipse-ee4j/mojarra/issues/4556
- https://github.com/eclipse-ee4j/mojarra/pull/4567
- https://github.com/eclipse-ee4j/mojarra/commit/8f70f2bd024f00ecd5b3dcca45df73edda29dcee
- https://github.com/eclipse-ee4j/mojarra/commit/a3fa9573789ed5e867c43ea38374f4dbd5a8f81f
- https://bugs.eclipse.org/bugs/show_bug.cgi?id=548244
- https://github.com/eclipse-ee4j/mojarra/compare/2.3.9-RELEASE...2.3.10-RELEASE
- https://github.com/eclipse-ee4j/mojarra/files/3039198/advisory.txt
- https://github.com/javaserverfaces/mojarra/compare/2.2.19...2.2.20
