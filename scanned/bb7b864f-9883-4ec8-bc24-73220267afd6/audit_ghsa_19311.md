# [H] **UNSUPPORTED WHEN ASSIGNED** GzipHandler causes part of request body to be seen as request body of a separate request

## Summary
Severity: High
Advisory: GHSA-q4rv-gq96-w7c5
CVE: CVE-2024-13009
CWE: CWE-404
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2025-05-08
Source: https://github.com/advisories/GHSA-q4rv-gq96-w7c5
Type: github-advisory

## Affected
- Maven: `org.eclipse.jetty:jetty-server` — affected >=9.4.0 <9.4.57.v20241219

## Details
In Eclipse Jetty versions 9.4.0 to 9.4.56 a buffer can be incorrectly released when confronted with a gzip error when inflating a request body. This can result in corrupted and/or inadvertent sharing of data between requests.

## References
- https://github.com/jetty/jetty.project/security/advisories/GHSA-q4rv-gq96-w7c5
- https://nvd.nist.gov/vuln/detail/CVE-2024-13009
- https://github.com/jetty/jetty.project
- https://gitlab.eclipse.org/security/cve-assignement/-/issues/48
