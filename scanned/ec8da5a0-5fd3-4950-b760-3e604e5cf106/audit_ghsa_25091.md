# [M] Cherry Music directory traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-q624-9634-77gh
CVE: CVE-2015-8309
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-q624-9634-77gh
Type: github-advisory

## Affected
- PyPI: `CherryMusic` — affected >=0 <0.36.0

## Details
Directory traversal vulnerability in Cherry Music before 0.36.0 allows remote authenticated users to read arbitrary files via the "value" parameter to "download."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-8309
- https://github.com/devsnd/cherrymusic/issues/598
- https://github.com/devsnd/cherrymusic/commit/62dec34a1ea0741400dd6b6c660d303dcd651e86
- https://github.com/devsnd/cherrymusic
- https://github.com/pypa/advisory-database/tree/main/vulns/cherrymusic/PYSEC-2017-99.yaml
- https://web.archive.org/web/20200227183321/http://www.securityfocus.com/bid/97149
- https://www.exploit-db.com/exploits/40361
- http://www.fomori.org/cherrymusic/Changes.html
