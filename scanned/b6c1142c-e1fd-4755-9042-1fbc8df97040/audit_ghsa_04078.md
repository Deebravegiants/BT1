# [M] Jupyter Notebook open redirect vulnerability

## Summary
Severity: Medium
Advisory: GHSA-rcx2-m7jp-p9wj
CVE: CVE-2019-10856
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-04-09
Source: https://github.com/advisories/GHSA-rcx2-m7jp-p9wj
Type: github-advisory

## Affected
- PyPI: `notebook` — affected >=0 <5.7.8

## Details
In Jupyter Notebook before 5.7.8, an open redirect can occur via an empty netloc. This issue exists because of an incomplete fix for CVE-2019-10255.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10856
- https://github.com/jupyter/notebook/commit/979e0bd15e794ceb00cc63737fcd5fd9addc4a99
- https://blog.jupyter.org/open-redirect-vulnerability-in-jupyter-jupyterhub-adf43583f1e4
- https://github.com/jupyter/notebook
- https://github.com/jupyter/notebook/compare/16cf97c...b8e30ea
- https://github.com/pypa/advisory-database/tree/main/vulns/notebook/PYSEC-2019-158.yaml
