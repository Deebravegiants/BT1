# [M] CVE-2025-50537

## Summary
Severity: Medium
Advisory: CVE-2025-50537
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-01-26
Source: https://osv.dev/vulnerability/CVE-2025-50537
Type: osv

## Details
Stack overflow vulnerability in eslint before 9.26.0 when serializing objects with circular references in eslint/lib/shared/serialization.js. The exploit is triggered via the RuleTester.run() method, which validates test cases and checks for duplicates. During validation, the internal function checkDuplicateTestCase() is called, which in turn uses the isSerializable() function for serialization checks. When a circular reference object is passed in, isSerializable() enters infinite recursion, ultimately causing a stack overflow.

## References
- https://gist.github.com/lyyffee/2ee1815e5c2da82c05e9838b9bfefbbc
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/50xxx/CVE-2025-50537.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-50537
- https://github.com/eslint/eslint/issues/19646
