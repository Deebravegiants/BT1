# [C] Radicale vulnerable to arbitrary file read or write

## Summary
Severity: Critical
Advisory: GHSA-fgqv-96v9-w23m
CVE: CVE-2015-8747
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-fgqv-96v9-w23m
Type: github-advisory

## Affected
- PyPI: `Radicale` — affected >=0 <1.1

## Details
The multifilesystem storage backend in Radicale before 1.1 allows remote attackers to read or write to arbitrary files via a crafted component name.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-8747
- https://github.com/Kozea/Radicale/pull/343
- https://github.com/Kozea/Radicale/commit/18c88642fb19ee1480690e51fff9605ecc6fdab5
- https://github.com/Unrud/Radicale/commit/bcaf452e516c02c9bed584a73736431c5e8831f1
- https://github.com/Kozea/Radicale
- https://github.com/pypa/advisory-database/tree/main/vulns/radicale/PYSEC-2016-36.yaml
- https://web.archive.org/web/20200804235922/http://www.securityfocus.com/bid/80255
- http://lists.fedoraproject.org/pipermail/package-announce/2016-January/175738.html
- http://lists.fedoraproject.org/pipermail/package-announce/2016-January/175776.html
- http://www.debian.org/security/2016/dsa-3462
- http://www.openwall.com/lists/oss-security/2016/01/05/7
- http://www.openwall.com/lists/oss-security/2016/01/06/4
- http://www.openwall.com/lists/oss-security/2016/01/06/7
