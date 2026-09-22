# [H] JupyterLab has an Extension Manager API/GUI Policy Discrepancy, allowing 3rd party (malicious) extensions install via POST request

## Summary
Severity: High
Advisory: GHSA-37w4-hwhx-4rc4
CVE: CVE-2026-42266
CWE: CWE-20, CWE-602, CWE-88
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-37w4-hwhx-4rc4
Type: github-advisory

## Affected
- PyPI: `jupyterlab` — affected >=4.0.0 <4.5.7

## Details
The allow-list of extensions that can be installed from PyPI Extension Manager (`allowed_extensions_uris`) is not correctly enforced by JupyterLab prior to 4.5.7. The PyPI Extension Manager was not contained to packages listed on the default PyPI index.

This has security implications for deployments that:
- have allow-listed specific extensions with aim to prevent users from installing packages
- have the kernel and terminals disabled or delegated to remote hosts (thus no access to install packages in the single-user server environment)
- have multi-tenant deployments that is not configured for untrusted users (as per documented on JupyterHub https://jupyterhub.readthedocs.io/en/5.2.1/explanation/websecurity.html)
- have the (default) PyPI Extension Manager enabled

### Impact

An authenticated attacker - such as a student in a shared JupyterHub environment or a user in a multi-tenant JupyterLab deployment - can escalate their privileges. This might allow for data exfiltration, lateral movement within the network, and persistent compromise of the server infrastructure.

### Patches

JupyterLab [`v4.5.7`](https://github.com/jupyterlab/jupyterlab/releases/tag/v4.5.7) contains the patch.

Users of applications that depend on JupyterLab, such as Notebook v7+, should update `jupyterlab` package too.

### Workarounds

Switch to read-only extension manager by adding the following command line option:

```bash
--LabApp.extension_manager=readonly
```

or the following traitlet:

```python
c.LabApp.extension_manager = 'readonly'
```

You can confirm that the read-only manager is in use from GUI:

<img width="293" height="293" alt="image" src="https://github.com/user-attachments/assets/8016c809-633e-4ed0-a5bc-6bc4793caa0f" />

Note: configuration of a PyPI proxy with allow-listed packages is not sufficient to protect from this vulnerability.

### References

- allow-list https://jupyterlab.readthedocs.io/en/stable/user/extensions.html#listing-configuration
- https://jupyterhub.readthedocs.io/en/5.2.1/explanation/websecurity.html
- https://jupyterlab.readthedocs.io/en/latest/user/extensions.html#extension-manager-implementations

## References
- https://github.com/jupyterlab/jupyterlab/security/advisories/GHSA-37w4-hwhx-4rc4
- https://nvd.nist.gov/vuln/detail/CVE-2026-42266
- https://github.com/jupyterlab/jupyterlab
- https://github.com/jupyterlab/jupyterlab/releases/tag/v4.5.7
- https://github.com/pypa/advisory-database/tree/main/vulns/jupyterlab/PYSEC-2026-164.yaml
- https://jupyterhub.readthedocs.io/en/5.2.1/explanation/websecurity.html
- https://jupyterlab.readthedocs.io/en/latest/user/extensions.html#extension-manager-implementations
