# [H] Flask-Cors Directory Traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-xc3p-ff3m-f46v
CVE: CVE-2020-25032
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-05-06
Source: https://github.com/advisories/GHSA-xc3p-ff3m-f46v
Type: github-advisory

## Affected
- PyPI: `Flask-Cors` — affected >=0 <3.0.9

## Details
An issue was discovered in Flask-CORS (aka CORS Middleware for Flask) before 3.0.9. It allows `../` directory traversal to access private resources because resource matching does not ensure that pathnames are in a canonical format.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25032
- https://github.com/corydolphin/flask-cors/commit/67c4b2cc98ae87cf1fa7df4f97fd81b40c79b895
- https://github.com/advisories/GHSA-xc3p-ff3m-f46v
- https://github.com/corydolphin/flask-cors
- https://github.com/corydolphin/flask-cors/releases/tag/3.0.9
- https://github.com/pypa/advisory-database/tree/main/vulns/flask-cors/PYSEC-2020-43.yaml
- https://www.debian.org/security/2020/dsa-4775
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00028.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00032.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00039.html
- http://lists.opensuse.org/opensuse-security-announce/2020-09/msg00048.html
