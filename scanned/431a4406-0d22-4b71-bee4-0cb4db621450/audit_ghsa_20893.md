# [H] mako is vulnerable to Regular Expression Denial of Service

## Summary
Severity: High
Advisory: GHSA-v973-fxgf-6xhp
CVE: CVE-2022-40023
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-v973-fxgf-6xhp
Type: github-advisory

## Affected
- PyPI: `mako` — affected >=0 <1.2.2

## Details
Sqlalchemy mako before 1.2.2 is vulnerable to Regular expression Denial of Service when using the Lexer class to parse. This also affects babelplugin and linguaplugin.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-40023
- https://github.com/sqlalchemy/mako/issues/366
- https://github.com/sqlalchemy/mako/commit/925760291d6efec64fda6e9dd1fd9cfbd5be068c
- https://github.com/advisories/GHSA-v973-fxgf-6xhp
- https://github.com/pypa/advisory-database/tree/main/vulns/mako/PYSEC-2022-260.yaml
- https://github.com/sqlalchemy/mako
- https://github.com/sqlalchemy/mako/blob/c2f392e0be52dc67d1b9770ab8cce6a9c736d547/mako/ext/extract.py#L21
- https://lists.debian.org/debian-lts-announce/2022/09/msg00026.html
- https://lists.debian.org/debian-lts-announce/2025/12/msg00004.html
- https://pyup.io/posts/pyup-discovers-redos-vulnerabilities-in-top-python-packages
- https://pyup.io/vulnerabilities/CVE-2022-40023/50870
