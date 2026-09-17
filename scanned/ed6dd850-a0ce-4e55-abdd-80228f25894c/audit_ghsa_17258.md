# [H] Logrus is vulnerable to DoS when using Entry.Writer()

## Summary
Severity: High
Advisory: GHSA-4f99-4q7p-p3gh
CVE: CVE-2025-65637
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-12-04
Source: https://github.com/advisories/GHSA-4f99-4q7p-p3gh
Type: github-advisory

## Affected
- Go: `github.com/sirupsen/logrus` — affected >=0 <1.8.3
- Go: `github.com/sirupsen/logrus` — affected >=1.9.0 <1.9.1
- Go: `github.com/sirupsen/logrus` — affected >=1.9.2 <1.9.3

## Details
A denial-of-service vulnerability exists in github.com/sirupsen/logrus when using Entry.Writer() to log a single-line payload larger than 64KB without newline characters. Due to limitations in the internal bufio.Scanner, the read fails with "token too long" and the writer pipe is closed, leaving Writer() unusable and causing application unavailability (DoS). This affects versions < 1.8.3, 1.9.0, and 1.9.2. The issue is fixed in 1.8.3, 1.9.1, and 1.9.3+, where the input is chunked and the writer continues to function even if an error is logged.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-65637
- https://github.com/sirupsen/logrus/issues/1370
- https://github.com/sirupsen/logrus/pull/1376
- https://github.com/sirupsen/logrus/commit/6acd903758687c4a3db3c11701e6c414fcf1c1f7
- https://github.com/mjuanxd/logrus-dos-poc
- https://github.com/mjuanxd/logrus-dos-poc/blob/main/README.md
- https://github.com/sirupsen/logrus
- https://github.com/sirupsen/logrus/releases/tag/v1.8.3
- https://github.com/sirupsen/logrus/releases/tag/v1.9.1
- https://github.com/sirupsen/logrus/releases/tag/v1.9.3
- https://security.snyk.io/vuln/SNYK-GOLANG-GITHUBCOMSIRUPSENLOGRUS-5564391
