# [M] JupyterLab: XSS due to lack of sanitization of the action attribute of an html <form>

## Summary
Severity: Medium
Advisory: GHSA-4952-p58q-6crx
CVE: CVE-2021-32797
CWE: CWE-75, CWE-79, CWE-87
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2021-08-23
Source: https://github.com/advisories/GHSA-4952-p58q-6crx
Type: github-advisory

## Affected
- PyPI: `jupyterlab` — affected >=0 <1.2.21
- PyPI: `jupyterlab` — affected >=2.0.0a0 <2.2.10
- PyPI: `jupyterlab` — affected >=2.3.0a0 <2.3.2
- PyPI: `jupyterlab` — affected >=3.0.0a0 <3.0.17
- PyPI: `jupyterlab` — affected >=3.1.0a0 <3.1.4
- PyPI: `notebook` — affected >=0 <5.7.11
- PyPI: `notebook` — affected >=6.0.0 <6.4.1

## Details
### Impact

Untrusted notebook can execute code on load. This is a remote code execution, but requires user action to open a notebook.

### Patches

Patched in the following versions: 3.1.4, 3.0.17, 2.3.2, 2.2.10, 1.2.21.

### References

[OWASP Page on Restricting Form Submissions](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html)

### For more information

If you have any questions or comments about this advisory, or vulnerabilities to report, please email our security list security@ipython.org.

Credit: Guillaume Jeanne from Google

## References
- https://github.com/google/security-research/security/advisories/GHSA-c469-p3jp-2vhx
- https://github.com/jupyterlab/jupyterlab/security/advisories/GHSA-4952-p58q-6crx
- https://nvd.nist.gov/vuln/detail/CVE-2021-32797
- https://github.com/jupyterlab/jupyterlab/commit/504825938c0abfa2fb8ff8d529308830a5ae42ed
- https://github.com/pypa/advisory-database/tree/main/vulns/jupyterlab/PYSEC-2021-130.yaml
