# [H] uWSGI Directory Traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-h2vm-c85r-5vh5
CVE: CVE-2018-7490
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-h2vm-c85r-5vh5
Type: github-advisory

## Affected
- PyPI: `uWSGI` — affected >=0 <2.0.17

## Details
uWSGI before 2.0.17 mishandles a `DOCUMENT_ROOT` check during use of the `--php-docroot` option, allowing directory traversal.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-7490
- https://github.com/unbit/uwsgi/commit/0a480f435ea6feb63deb410ad2bf376ed3f05f8a
- https://github.com/pypa/advisory-database/tree/main/vulns/uwsgi/PYSEC-2018-78.yaml
- https://github.com/unbit/uwsgi
- https://uwsgi-docs.readthedocs.io/en/latest/Changelog-2.0.17.html
- https://www.debian.org/security/2018/dsa-4142
- https://www.exploit-db.com/exploits/44223
