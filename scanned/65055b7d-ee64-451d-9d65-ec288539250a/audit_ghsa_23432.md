# [C] JFinal Java Deserialization Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-h3j8-fr5q-8rfr
CVE: CVE-2021-31649
CWE: CWE-502
Ecosystem: Maven
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-h3j8-fr5q-8rfr
Type: github-advisory

## Affected
- Maven: `com.jfinal:jfinal` — affected >=0

## Details
In applications using jfinal 4.9.08 and below, there is a deserialization vulnerability when using redis which can lead to remote code execution

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-31649
- https://github.com/jfinal/jfinal/issues/184
- http://note.youdao.com/noteshare?id=787ccbb8345dbd4a905aebe35f1d8aa8&sub=6C5C072C901949429EFD978405212FA4
