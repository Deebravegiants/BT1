# [M] Eclipse Glassfish URL redirection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-7gq2-vwq9-w8vw
CVE: CVE-2024-8646
CWE: CWE-601
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-09-11
Source: https://github.com/advisories/GHSA-7gq2-vwq9-w8vw
Type: github-advisory

## Affected
- Maven: `org.glassfish.main.web:web-core` — affected >=0 <7.0.10

## Details
In Eclipse Glassfish versions prior to 7.0.10, a URL redirection vulnerability to untrusted sites existed.
This vulnerability is caused by the vulnerability (CVE-2023-41080) in the Apache code included in GlassFish.
This vulnerability only affects applications that are explicitly deployed to the root context ('/').

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-8646
- https://github.com/eclipse-ee4j/glassfish/pull/24655
- https://github.com/eclipse-ee4j/glassfish/commit/06b80012761d07f6e40e40aa6b0133465b0bd145
- https://github.com/eclipse-ee4j/glassfish
- https://gitlab.eclipse.org/security/cve-assignement/-/issues/34
- https://gitlab.eclipse.org/security/vulnerability-reports/-/issues/163
- https://glassfish.org/download
