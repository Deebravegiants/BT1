# [H] Unsecured endpoints in the jupyter-lsp server extension

## Summary
Severity: High
Advisory: GHSA-4qhp-652w-c22x
CVE: CVE-2024-22415
CWE: CWE-22, CWE-23
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2024-01-18
Source: https://github.com/advisories/GHSA-4qhp-652w-c22x
Type: github-advisory

## Affected
- PyPI: `jupyter-lsp` — affected >=0 <2.2.2

## Details
### Impact
Installations of jupyter-lsp running in environments without configured file system access control (on the operating system level), and with jupyter-server instances exposed to non-trusted network are vulnerable to unauthorised access and modification of file system beyond the jupyter root directory.

### Patches
Version 2.2.2 has been patched.

### Workarounds
Users of jupyterlab who do not use jupyterlab-lsp can uninstall jupyter-lsp.

### Credits
We would like to credit Bary Levy, researcher of pillar.security research team, for the discovery and responsible disclosure of this vulnerability.

Edit: based on advice from pillar.security the Confidentiality/Integrity/Availability were increased to High to reflect potential for critical impact on publicly hosted jupyter-server instances lacking isolation of user privileges on operating system level (for best practices please consult https://jupyterhub.readthedocs.io/en/stable/explanation/websecurity.html#protect-users-from-each-other) and CWE-94 was added due to a potential vulnerability chaining in specific environments.

## References
- https://github.com/jupyter-lsp/jupyterlab-lsp/security/advisories/GHSA-4qhp-652w-c22x
- https://nvd.nist.gov/vuln/detail/CVE-2024-22415
- https://github.com/jupyter-lsp/jupyterlab-lsp/commit/4ad12f204ad0b85580fc32137c647baaff044e95
- https://github.com/jupyter-lsp/jupyterlab-lsp
- https://github.com/jupyter-lsp/jupyterlab-lsp/releases/tag/v5.0.2
