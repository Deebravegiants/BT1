# [M] Dynamic-Datasource has an Injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-6rmm-pg23-5f8q
CVE: CVE-2026-7045
CWE: CWE-74
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-27
Source: https://github.com/advisories/GHSA-6rmm-pg23-5f8q
Type: github-advisory

## Affected
- Maven: `com.baomidou:dynamic-datasource-spring` — affected >=0

## Details
A vulnerability was determined in baomidou dynamic-datasource 2.5.0. Affected by this vulnerability is the function DsSpelExpressionProcessor#doDetermineDatasource of the file dynamic-datasource-spring/src/main/java/com/baomidou/dynamic/datasource/processor/DsSpelExpressionProcessor.java of the component StandardEvaluationContext/SpelExpressionParser. This manipulation causes injection. The attack may be initiated remotely. Patch name: 273fcedaee984c08197c0890f14190b86ab7e0b8. It is recommended to apply a patch to fix this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7045
- https://github.com/baomidou/dynamic-datasource/issues/766
- https://github.com/baomidou/dynamic-datasource/pull/767
- https://github.com/baomidou/dynamic-datasource/commit/273fcedaee984c08197c0890f14190b86ab7e0b8
- https://github.com/baomidou/dynamic-datasource
- https://vuldb.com/submit/798600
- https://vuldb.com/vuln/359624
- https://vuldb.com/vuln/359624/cti
