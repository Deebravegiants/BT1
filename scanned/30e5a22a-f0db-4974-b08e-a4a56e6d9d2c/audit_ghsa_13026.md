# [H] Denial of service in jackson-dataformat-toml

## Summary
Severity: High
Advisory: GHSA-rg2c-cfxv-qp6f
CVE: CVE-2023-3894
CWE: CWE-20, CWE-400, CWE-787
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2023-08-08
Source: https://github.com/advisories/GHSA-rg2c-cfxv-qp6f
Type: github-advisory

## Affected
- Maven: `com.fasterxml.jackson.dataformat:jackson-dataformat-toml` — affected >=0 <2.15.0

## Details
Those using jackson-dataformats-text to parse TOML data may be vulnerable to Denial of Service attacks (DOS). If the parser is running on user supplied input, an attacker may supply content that causes the parser to crash by stackoverflow. This effect may support a denial of service attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-3894
- https://github.com/FasterXML/jackson-dataformats-text/pull/398
- https://github.com/FasterXML/jackson-dataformats-text/commit/5dd5f740aedcf37adad7ffece460e75e54abb0ed
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=50083
- https://github.com/FasterXML/jackson-dataformats-text
- https://github.com/FasterXML/jackson-dataformats-text/blob/2.16/release-notes/VERSION-2.x
