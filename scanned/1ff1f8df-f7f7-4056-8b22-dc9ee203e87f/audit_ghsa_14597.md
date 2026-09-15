# [H] Apache UIMA DUCC allows remote code execution 

## Summary
Severity: High
Advisory: GHSA-34m5-796p-mjcp
CVE: CVE-2023-28935
CWE: CWE-77
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-30
Source: https://github.com/advisories/GHSA-34m5-796p-mjcp
Type: github-advisory

## Affected
- Maven: `org.apache.uima:uima-ducc-parent` — affected >=0

## Details
** UNSUPPORTED WHEN ASSIGNED ** Improper Neutralization of Special Elements used in a Command ('Command Injection') vulnerability in Apache Software Foundation Apache UIMA DUCC. When using the "Distributed UIMA Cluster Computing" (DUCC) module of Apache UIMA, an authenticated user that has the permissions to modify core entities can cause command execution as the system user that runs the web process. As the "Distributed UIMA Cluster Computing" module for UIMA is retired, we do not plan to release a fix for this issue. NOTE: This vulnerability only affects products that are no longer supported by the maintainer.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-28935
- https://github.com/apache/uima-ducc
- https://lists.apache.org/thread/r19z14b9rrfxv72r93q5trq5tyffo75g
