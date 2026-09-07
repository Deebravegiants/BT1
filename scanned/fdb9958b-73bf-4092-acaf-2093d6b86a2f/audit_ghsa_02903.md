# [M] Stored XSS in Jupyter nbdime

## Summary
Severity: Medium
Advisory: GHSA-p6rw-44q7-3fw4
CVE: CVE-2021-41134
CWE: CWE-79
Ecosystem: PyPI, npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2021-11-08
Source: https://github.com/advisories/GHSA-p6rw-44q7-3fw4
Type: github-advisory

## Affected
- PyPI: `nbdime` — affected >=0 <1.1.1
- PyPI: `nbdime` — affected >=2.0.0 <2.1.1
- PyPI: `nbdime` — affected >=3.0.0 <3.1.1
- npm: `nbdime` — affected >=0 <5.0.2
- npm: `nbdime` — affected >=6.0.0 <6.1.2
- npm: `nbdime-jupyterlab` — affected >=0 <1.0.1
- npm: `nbdime-jupyterlab` — affected >=2.0.0 <2.1.1

## Details
### Impact

Improper handling of user controlled input caused a stored cross-site scripting (XSS) vulnerability. All previous versions of nbdime are affected.

### Patches

Security patches will be released for each of the major versions of the nbdime packages since version 1.x of the nbdime python package.

#### Python
- nbdime 1.x: Patched in v. 1.1.1
- nbdime 2.x: Patched in v. 2.1.1
- nbdime 3.x: Patched in v. 3.1.1

#### npm
- nbdime 6.x version: Patched in 6.1.2
- nbdime 5.x version: Patched in 5.0.2
- nbdime-jupyterlab 1.x version: Patched in 1.0.1
- nbdime-jupyterlab 2.x version: Patched in 2.1.1

### For more information
If you have any questions or comments about this advisory email us at [security@ipython.org](mailto:security@ipython.org).

## References
- https://github.com/jupyter/nbdime/security/advisories/GHSA-p6rw-44q7-3fw4
- https://nvd.nist.gov/vuln/detail/CVE-2021-41134
- https://github.com/jupyter/nbdime/commit/e44a5cc7677f24b45ebafc756db49058c2f750ea
- https://github.com/jupyter/nbdime
- https://github.com/pypa/advisory-database/tree/main/vulns/nbdime/PYSEC-2021-428.yaml
