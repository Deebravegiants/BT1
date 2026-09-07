# [H] Esoteric YamlBeans Unsafe Deserialization vulnerability

## Summary
Severity: High
Advisory: GHSA-jm7r-4pg6-gf26
CVE: CVE-2023-24621
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-08-25
Source: https://github.com/advisories/GHSA-jm7r-4pg6-gf26
Type: github-advisory

## Affected
- Maven: `com.esotericsoftware.yamlbeans:yamlbeans` — affected >=0

## Details
An issue was discovered in Esoteric YamlBeans through 1.15. It allows untrusted deserialisation to Java classes by default, where the data and class are controlled by the author of the YAML document being processed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24621
- https://contrastsecurity.com
- https://github.com/Contrast-Security-OSS/yamlbeans/blob/main/SECURITY.md
- https://github.com/EsotericSoftware
- https://github.com/EsotericSoftware/yamlbeans
