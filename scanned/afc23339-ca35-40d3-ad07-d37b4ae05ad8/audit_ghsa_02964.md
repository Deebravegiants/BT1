# [M] incomplete JupyterHub logout with simultaneous JupyterLab sessions

## Summary
Severity: Medium
Advisory: GHSA-cw7p-q79f-m2v7
CVE: CVE-2021-41247
CWE: CWE-613
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2021-11-08
Source: https://github.com/advisories/GHSA-cw7p-q79f-m2v7
Type: github-advisory

## Affected
- PyPI: `jupyterhub` — affected >=1.0.0 <1.5.0

## Details
### Impact

Users of JupyterLab with JupyterHub who have multiple JupyterLab tabs open in the same browser session, may see incomplete logout from the single-user server, as fresh credentials (for the single-user server only, not the Hub) reinstated after logout, if another active JupyterLab session is open while the logout takes place.

### Patches

Upgrade to JupyterHub 1.5. For distributed deployments, it is jupyterhub in the _user_ environment that needs patching. There are no patches necessary in the Hub environment.

### Workarounds

The only workaround is to make sure that only one JupyterLab tab is open when you log out.

## References
- https://github.com/jupyterhub/jupyterhub/security/advisories/GHSA-cw7p-q79f-m2v7
- https://nvd.nist.gov/vuln/detail/CVE-2021-41247
- https://github.com/jupyterhub/jupyterhub/commit/5ac9e7f73a6e1020ffddc40321fc53336829fe27
- https://github.com/jupyterhub/jupyterhub
- https://github.com/pypa/advisory-database/tree/main/vulns/jupyterhub/PYSEC-2021-386.yaml
