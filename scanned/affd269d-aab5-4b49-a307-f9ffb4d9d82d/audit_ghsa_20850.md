# [M] snakeYAML before 1.31 vulnerable to Denial of Service due to Out-of-bounds Write

## Summary
Severity: Medium
Advisory: GHSA-98wm-3w3q-mw94
CVE: CVE-2022-38751
CWE: CWE-121, CWE-787
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-06
Source: https://github.com/advisories/GHSA-98wm-3w3q-mw94
Type: github-advisory

## Affected
- Maven: `org.yaml:snakeyaml` — affected >=0 <1.31

## Details
Using snakeYAML to parse untrusted YAML files may be vulnerable to Denial of Service attacks (DOS). If the parser is running on user supplied input, an attacker may supply content that causes the parser to crash by stackoverflow.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-38751
- https://bitbucket.org/snakeyaml/snakeyaml
- https://bitbucket.org/snakeyaml/snakeyaml/issues/530/stackoverflow-oss-fuzz-47039
- https://bitbucket.org/snakeyaml/snakeyaml/src/master/src/test/java/org/yaml/snakeyaml/issues/issue530/Fuzzy47039Test.java
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=47039
- https://lists.debian.org/debian-lts-announce/2022/10/msg00001.html
- https://security.gentoo.org/glsa/202305-28
- https://security.netapp.com/advisory/ntap-20240315-0010
