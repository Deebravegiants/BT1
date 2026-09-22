# [M] Jettison parser crash by stackoverflow

## Summary
Severity: Medium
Advisory: GHSA-xqcq-j8w9-3pxv
CWE: CWE-121, CWE-787
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-08-01
Source: https://github.com/advisories/GHSA-xqcq-j8w9-3pxv
Type: github-advisory

## Affected
- Maven: `com.tencyle.fixes:org.codehaus.jettison--jettison` — affected 1.1-tencyle-2.1.0

## Details
Those using Jettison to parse untrusted XML or JSON data may be vulnerable to Denial of Service attacks (DOS). If the parser is running on user supplied input, an attacker may supply content that causes the parser to crash by stackoverflow. This effect may support a denial of service attack.

### References

- https://nvd.nist.gov/vuln/detail/CVE-2022-40149
- https://github.com/jettison-json/jettison/issues/45
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=46538
- https://github.com/jettison-json/jettison/pull/49/files
- https://github.com/jettison-json/jettison/releases/tag/jettison-1.5.1
- https://lists.debian.org/debian-lts-announce/2022/11/msg00011.html
- https://www.debian.org/security/2023/dsa-5312

## References
- https://github.com/tencyle-fixes/jettison/security/advisories/GHSA-xqcq-j8w9-3pxv
- https://nvd.nist.gov/vuln/detail/CVE-2022-40149
- https://github.com/jettison-json/jettison/issues/45
- https://github.com/jettison-json/jettison/pull/49
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=46538
- https://github.com/jettison-json/jettison/releases/tag/jettison-1.5.1
- https://github.com/tencyle-fixes/jettison
- https://github.com/tencyle-fixes/jettison#jettison-backports-repository-by-tencyle
- https://lists.debian.org/debian-lts-announce/2022/11/msg00011.html
- https://www.debian.org/security/2023/dsa-5312
