# [H] Gunicorn contains Improper Neutralization of CRLF sequences in HTTP headers

## Summary
Severity: High
Advisory: GHSA-32pc-xphx-q4f6
CVE: CVE-2018-1000164
CWE: CWE-93
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2018-07-12
Source: https://github.com/advisories/GHSA-32pc-xphx-q4f6
Type: github-advisory

## Affected
- PyPI: `gunicorn` — affected >=0 <19.5.0

## Details
gunicorn version 19.4.5 contains a CWE-113: Improper Neutralization of CRLF Sequences in HTTP Headers vulnerability in "process_headers" function in "gunicorn/http/wsgi.py" that can result in an attacker causing the server to return arbitrary HTTP headers. This vulnerability appears to have been fixed in 19.5.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000164
- https://github.com/benoitc/gunicorn/issues/1227
- https://epadillas.github.io/2018/04/02/http-header-splitting-in-gunicorn-19.4.5
- https://github.com/advisories/GHSA-32pc-xphx-q4f6
- https://github.com/benoitc/gunicorn
- https://github.com/pypa/advisory-database/tree/main/vulns/gunicorn/PYSEC-2018-55.yaml
- https://lists.debian.org/debian-lts-announce/2018/04/msg00022.html
- https://usn.ubuntu.com/4022-1
- https://www.debian.org/security/2018/dsa-4186
