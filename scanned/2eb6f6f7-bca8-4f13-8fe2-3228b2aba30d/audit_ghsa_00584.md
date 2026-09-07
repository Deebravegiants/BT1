# [M] Jupyter Notebook XSS via directory name

## Summary
Severity: Medium
Advisory: GHSA-3p4q-x8f3-p7vq
CVE: CVE-2018-19352
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2018-11-21
Source: https://github.com/advisories/GHSA-3p4q-x8f3-p7vq
Type: github-advisory

## Affected
- PyPI: `notebook` — affected >=0 <5.7.2

## Details
Jupyter Notebook before 5.7.2 allows XSS via a crafted directory name because notebook/static/tree/js/notebooklist.js handles certain URLs unsafely.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-19352
- https://github.com/jupyter/notebook/commit/288b73e1edbf527740e273fcc69b889460871648
- https://github.com/jupyter/notebook
- https://github.com/jupyter/notebook/blob/master/docs/source/changelog.rst
- https://github.com/pypa/advisory-database/tree/main/vulns/notebook/PYSEC-2018-18.yaml
- https://pypi.org/project/notebook/#history
