# [M] Open Redirect vulnerability in jupyterhub and notebook

## Summary
Severity: Medium
Advisory: GHSA-rv62-4pmj-xw6h
CVE: CVE-2019-10255
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-04-02
Source: https://github.com/advisories/GHSA-rv62-4pmj-xw6h
Type: github-advisory

## Affected
- PyPI: `notebook` — affected >=0 <5.7.8
- PyPI: `jupyterhub` — affected >=0 <0.9.6

## Details
An Open Redirect vulnerability for all browsers in Jupyter Notebook before 5.7.8 and some browsers (Chrome, Firefox) in JupyterHub before 0.9.6 allows crafted links to the login page, which will redirect to a malicious site after successful login. Servers running on a base_url prefix are not affected.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-10255
- https://github.com/jupyter/notebook/commit/08c4c898182edbe97aadef1815cce50448f975cb
- https://github.com/jupyter/notebook/commit/70fe9f0ddb3023162ece21fbb77d5564306b913b
- https://github.com/jupyter/notebook/commit/d65328d4841892b412aef9015165db1eb029a8ed
- https://blog.jupyter.org/open-redirect-vulnerability-in-jupyter-jupyterhub-adf43583f1e4
- https://github.com/advisories/GHSA-rv62-4pmj-xw6h
- https://github.com/jupyter/notebook
- https://github.com/jupyter/notebook/compare/05aa4b2...16cf97c
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UP5RLEES2JBBNSNLBR65XM6PCD4EMF7D
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/VMDPJBVXOVO6LYGAT46VZNHH6JKSCURO
