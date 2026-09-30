# [C] Eclipse BaSyx Java Server SDK vulnerable to Path Traversal

## Summary
Severity: Critical
Advisory: GHSA-8gpm-h2mh-36qc
CVE: CVE-2026-7411
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-8gpm-h2mh-36qc
Type: github-advisory

## Affected
- Maven: `org.eclipse.basyx:basyx.sdk` — affected >=0 <2.0.0-milestone-10

## Details
In Eclipse BaSyx Java Server SDK versions prior to 2.0.0-milestone-10, inadequate path normalization in the Submodel HTTP API allows an unauthenticated remote attacker to perform a path traversal attack. By supplying a maliciously crafted fileName parameter during a file upload operation, an attacker can bypass intended storage boundaries and write arbitrary files to any location on the host filesystem accessible by the Java process. This can lead to Remote Code Execution (RCE) and complete system compromise.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7411
- https://github.com/eclipse-basyx/basyx-java-sdk
- https://gitlab.eclipse.org/security/cve-assignment/-/issues/102
- https://gitlab.eclipse.org/security/vulnerability-reports/-/issues/423
