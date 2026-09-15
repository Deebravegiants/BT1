# [M] DoS in SnakeYAML

## Summary
Severity: Medium
Advisory: CVE-2022-38749
Aliases: GHSA-c4r9-r8fh-9vj2
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2022-09-05
Source: https://osv.dev/vulnerability/CVE-2022-38749
Type: osv

## Details
Using snakeYAML to parse untrusted YAML files may be vulnerable to Denial of Service attacks (DOS). If the parser is running on user supplied input, an attacker may supply content that causes the parser to crash by stackoverflow.

## References
- https://bitbucket.org/snakeyaml/snakeyaml/issues/525/got-stackoverflowerror-for-many-open
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=47024
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/38xxx/CVE-2022-38749.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-38749
- https://security.gentoo.org/glsa/202305-28
- https://security.netapp.com/advisory/ntap-20240315-0010/
- https://lists.debian.org/debian-lts-announce/2022/10/msg00001.html
