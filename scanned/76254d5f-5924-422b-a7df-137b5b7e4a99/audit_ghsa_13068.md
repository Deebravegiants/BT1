# [M] Esoteric YamlBeans XML Entity Expansion vulnerability

## Summary
Severity: Medium
Advisory: GHSA-vj49-j7rc-h54f
CVE: CVE-2023-24620
CWE: CWE-400, CWE-611
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-08-25
Source: https://github.com/advisories/GHSA-vj49-j7rc-h54f
Type: github-advisory

## Affected
- Maven: `com.esotericsoftware.yamlbeans:yamlbeans` — affected >=0

## Details
An issue was discovered in Esoteric YamlBeans through 1.15. A crafted YAML document is able perform am XML Entity Expansion attack against YamlBeans YamlReader. By exploiting the Anchor feature in YAML, it is possible to generate a small YAML document that, when read, is expanded to a large size, causing CPU and memory consumption, such as a Java Out-of-Memory exception.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-24620
- https://contrastsecurity.com
- https://github.com/Contrast-Security-OSS/yamlbeans/blob/main/SECURITY.md
- https://github.com/EsotericSoftware
- https://github.com/EsotericSoftware/yamlbeans
