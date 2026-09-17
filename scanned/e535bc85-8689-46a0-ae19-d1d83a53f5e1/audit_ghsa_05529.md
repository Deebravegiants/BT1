# [M] binary-parser library has a code injection vulnerability

## Summary
Severity: Medium
Advisory: GHSA-m39p-34qh-rh3w
CVE: CVE-2026-1245
CWE: CWE-94
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-01-20
Source: https://github.com/advisories/GHSA-m39p-34qh-rh3w
Type: github-advisory

## Affected
- npm: `binary-parser` — affected >=0 <2.3.0

## Details
A code injection vulnerability in the binary-parser library prior to version 2.3.0 allows arbitrary JavaScript code execution when untrusted values are used in parser field names or encoding parameters. The library directly interpolates these values into dynamically generated code without sanitization, enabling attackers to execute arbitrary code in the context of the Node.js process.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-1245
- https://github.com/keichi/binary-parser/pull/283
- https://github.com/keichi/binary-parser
- https://kb.cert.org/vuls/id/102648
- https://www.cve.org/CVERecord?id=CVE-2026-1245
- https://www.kb.cert.org/vuls/id/102648
- https://www.npmjs.com/package/binary-parser
