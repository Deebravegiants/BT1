# [M] Radicale regex metacharacters injection in the user name

## Summary
Severity: Medium
Advisory: GHSA-6w8c-6jrg-qwj2
CVE: CVE-2015-8748
CWE: CWE-74
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-6w8c-6jrg-qwj2
Type: github-advisory

## Affected
- PyPI: `Radicale` — affected >=0 <1.1

## Details
Radicale before 1.1 allows remote authenticated users to bypass `owner_write` and `owner_only` limitations via regex metacharacters in the user name, as demonstrated by `.*`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-8748
- https://github.com/Kozea/Radicale/pull/341
- https://github.com/Kozea/Radicale/commit/1109973a925970353dfd13c6df8de0e4e446d983
- https://github.com/Unrud/Radicale/commit/4bfe7c9f7991d534c8b9fbe153af9d341f925f98
- https://github.com/Kozea/Radicale
- https://github.com/pypa/advisory-database/tree/main/vulns/radicale/PYSEC-2016-37.yaml
- https://pypi.org/project/radicale
- https://web.archive.org/web/20200804235922/http://www.securityfocus.com/bid/80255
- http://lists.fedoraproject.org/pipermail/package-announce/2016-January/175738.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-January/175776.html
- http://www.debian.org/security/2016/dsa-3462
- http://www.openwall.com/lists/oss-security/2016/01/05/7
- http://www.openwall.com/lists/oss-security/2016/01/06/4
