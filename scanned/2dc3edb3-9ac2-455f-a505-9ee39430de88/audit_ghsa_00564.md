# [M] Jupyter Notebook XSS via untrusted notebooks

## Summary
Severity: Medium
Advisory: GHSA-49qr-xh3w-h436
CVE: CVE-2018-19351
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-11-21
Source: https://github.com/advisories/GHSA-49qr-xh3w-h436
Type: github-advisory

## Affected
- PyPI: `notebook` — affected >=0 <5.7.1

## Details
Jupyter Notebook before 5.7.1 allows XSS via an untrusted notebook because nbconvert responses are considered to have the same origin as the notebook server. In other words, nbconvert endpoints can execute JavaScript with access to the server API. In notebook/nbconvert/handlers.py, NbconvertFileHandler and NbconvertPostHandler do not set a Content Security Policy to prevent this.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-19351
- https://github.com/jupyter/notebook/commit/107a89fce5f413fb5728c1c5d2c7788e1fb17491
- https://github.com/jupyter/notebook
- https://github.com/jupyter/notebook/blob/master/docs/source/changelog.rst
- https://github.com/pypa/advisory-database/tree/main/vulns/notebook/PYSEC-2018-17.yaml
- https://groups.google.com/forum/#!topic/jupyter/hWzu2BSsplY
- https://lists.debian.org/debian-lts-announce/2020/11/msg00033.html
- https://pypi.org/project/notebook/#history
