# [C] Eclipse Parsson stack overflow when parsing deeply nested input

## Summary
Severity: Critical
Advisory: GHSA-2rwm-xv5j-777p
CVE: CVE-2023-7272
CWE: CWE-787
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2024-07-17
Source: https://github.com/advisories/GHSA-2rwm-xv5j-777p
Type: github-advisory

## Affected
- Maven: `org.eclipse.parsson:parsson` — affected >=1.1.0 <1.1.3
- Maven: `org.eclipse.parsson:parsson` — affected >=0 <1.0.4

## Details
In Eclipse Parsson before 1.0.4 and 1.1.3, a document with a large depth of nested objects can allow an attacker to cause a Java stack overflow exception and denial of service. Eclipse Parsson allows processing (e.g. parse, generate, transform and query) JSON documents.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-7272
- https://github.com/eclipse-ee4j/parsson/issues/91
- https://github.com/eclipse-ee4j/parsson/commit/755d2a86dff74fecc4114fbe7d21e071380c4e45
- https://github.com/eclipse-ee4j/parsson/commit/d0ec79badd44a940c82842954430762a2199f4e1
- https://github.com/eclipse-ee4j/parsson
- https://gitlab.eclipse.org/security/vulnerability-reports/-/issues/12
