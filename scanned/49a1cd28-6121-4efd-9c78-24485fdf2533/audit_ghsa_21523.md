# [M] Snakeyaml vulnerable to Stack overflow leading to denial of service

## Summary
Severity: Medium
Advisory: GHSA-w37g-rhq8-7m4j
CVE: CVE-2022-41854
CWE: CWE-121, CWE-787
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-11
Source: https://github.com/advisories/GHSA-w37g-rhq8-7m4j
Type: github-advisory

## Affected
- Maven: `org.yaml:snakeyaml` — affected >=0 <1.32

## Details
Those using Snakeyaml to parse untrusted YAML files may be vulnerable to Denial of Service attacks (DOS). If the parser is running on user supplied input, an attacker may supply content that causes the parser to crash by stack overflow. This effect may support a denial of service attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41854
- https://bitbucket.org/snakeyaml/snakeyaml
- https://bitbucket.org/snakeyaml/snakeyaml/commits/e230a1758842beec93d28eddfde568c21774780a
- https://bitbucket.org/snakeyaml/snakeyaml/issues/531
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=50355
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3DDXEXXWAZGF5AVHIPGFPXIWL6TSMKJE
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/7MKE4XWRXTH32757H7QJU4ACS67DYDCR
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/KSPAJ5Y45A4ZDION2KN5RDWLHK4XKY2J
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/3DDXEXXWAZGF5AVHIPGFPXIWL6TSMKJE
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7MKE4XWRXTH32757H7QJU4ACS67DYDCR
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/KSPAJ5Y45A4ZDION2KN5RDWLHK4XKY2J
- https://security.netapp.com/advisory/ntap-20240315-0009
- https://security.netapp.com/advisory/ntap-20240621-0006
