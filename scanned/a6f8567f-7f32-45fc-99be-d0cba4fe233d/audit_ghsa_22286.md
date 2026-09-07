# [M] http before 0.13.3 vulnerable to header injection

## Summary
Severity: Medium
Advisory: GHSA-4rgh-jx4f-qfcq
CVE: CVE-2020-35669
CWE: CWE-74
Ecosystem: Pub
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-4rgh-jx4f-qfcq
Type: github-advisory

## Affected
- Pub: `http` — affected >=0 <0.13.3

## Details
An issue was discovered in the http package before 0.13.3 for Dart. If the attacker controls the HTTP method and the app is using Request directly, it's possible to achieve CRLF injection in an HTTP request via HTTP header injection. This issue has been addressed in commit abb2bb182 by validating request methods.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-35669
- https://github.com/dart-lang/http/issues/511
- https://github.com/dart-lang/http/pull/512
- https://github.com/dart-lang/http/commit/abb2bb182fbd7f03aafd1f889b902d7b3bdb8769
- https://github.com/dart-lang/http
- https://github.com/dart-lang/http/blob/master/CHANGELOG.md#0133
- https://pub.dev/packages/http/changelog#0133
