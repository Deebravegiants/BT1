# [H] user-readable api tokens in systemd units for JupyterHub

## Summary
Severity: High
Advisory: GHSA-cg54-gpgr-4rm6
CVE: CVE-2020-26261
CWE: CWE-668
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2020-12-09
Source: https://github.com/advisories/GHSA-cg54-gpgr-4rm6
Type: github-advisory

## Affected
- PyPI: `jupyterhub-systemdspawner` — affected >=0 <0.15.0

## Details
### Impact
user API tokens issued to single-user servers are specified in the environment of systemd units, which are accessible to all users.

In particular, the-littlest-jupyterhub is affected, which uses systemdspawner by default.

### Patches
Patched in jupyterhub-systemdspawner v0.15

### Workarounds
No workaround other than upgrading systemdspawner to 0.15

### For more information

If you have any questions or comments about this advisory:
* Open a thread in [the Jupyter forum](https://discourse.jupyter.org)
* Email us at [security@ipython.org](mailto:security@ipython.org)

## References
- https://github.com/jupyterhub/systemdspawner/security/advisories/GHSA-cg54-gpgr-4rm6
- https://nvd.nist.gov/vuln/detail/CVE-2020-26261
- https://github.com/jupyterhub/systemdspawner/commit/a4d08fd2ade1cfd0ef2c29dc221e649345f23580
- https://github.com/jupyterhub/systemdspawner
- https://github.com/jupyterhub/systemdspawner/blob/master/CHANGELOG.md#v015
- https://github.com/pypa/advisory-database/tree/main/vulns/jupyterhub-systemdspawner/PYSEC-2020-52.yaml
- https://pypi.org/project/jupyterhub-systemdspawner
