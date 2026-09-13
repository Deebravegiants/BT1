# [H] Apache ORC vulnerable to Uncontrolled Recursion

## Summary
Severity: High
Advisory: GHSA-mqmp-4mcp-vg8v
CVE: CVE-2018-8015
CWE: CWE-674
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-mqmp-4mcp-vg8v
Type: github-advisory

## Affected
- Maven: `org.apache.orc:orc` — affected >=1.0.0 <1.4.4

## Details
In Apache ORC 1.0.0 to 1.4.3 a malformed ORC file can trigger an endlessly recursive function call in the C++ or Java parser. The impact of this bug is most likely denial-of-service against software that uses the ORC file parser. With the C++ parser, the stack overflow might possibly corrupt the stack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-8015
- https://github.com/apache/orc/pull/266
- https://github.com/apache/orc/commit/d5018d309a8adc6b8e0567cb692a17371d16e108
- https://github.com/apache/orc
- https://github.com/apache/orc/blob/9cf9d26a20ac4d43911d7967ecaef8ef26b60594/site/security/CVE-2018-8015.md
- https://github.com/apache/orc/commits/rel/release-1.4.4
- https://orc.apache.org/security/CVE-2018-8015
