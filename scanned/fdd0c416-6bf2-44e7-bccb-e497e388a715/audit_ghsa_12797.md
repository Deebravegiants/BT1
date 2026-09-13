# [M] Java Merge-sort Insecure Temporary File vulnerability

## Summary
Severity: Medium
Advisory: GHSA-qxxc-7mq4-mf79
CVE: CVE-2022-24913
CWE: CWE-377, CWE-668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-01-12
Source: https://github.com/advisories/GHSA-qxxc-7mq4-mf79
Type: github-advisory

## Affected
- Maven: `com.fasterxml.util:java-merge-sort` — affected >=0 <1.1.0

## Details
Versions of the package `com.fasterxml.util:java-merge-sort` before 1.1.0 are vulnerable to Insecure Temporary File in the `StdTempFileProvider()` function in `StdTempFileProvider.java`, which uses the permissive `File.createTempFile()` function, exposing temporary file contents.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-24913
- https://github.com/cowtowncoder/java-merge-sort/pull/21
- https://github.com/cowtowncoder/java-merge-sort/commit/450fdee70b5f181c2afc5d817f293efa1a543902
- https://github.com/cowtowncoder/java-merge-sort
- https://security.snyk.io/vuln/SNYK-JAVA-COMFASTERXMLUTIL-3227926
