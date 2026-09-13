# [C] JupyterLab before 4.6.2 Authentication Bypass via PyPIExtensionManager

## Summary
Severity: Critical
Advisory: CVE-2026-73626
Aliases: GHSA-whvh-wf3x-g77j
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-73626
Type: osv

## Details
JupyterLab versions >=4.6.0,<=4.6.1 and <=4.5.9 contain an allowlist/blocklist enforcement gap in PyPIExtensionManager.install(). A missing 'await' caused the is_install_allowed coroutine to never execute, so the extension allowlist/blocklist check was not enforced for direct callers of install(). The stock JupyterLab HTTP API and Extension Manager UI are not affected, as they perform a separate, correctly awaited check. The issue affects only deployments where a custom extension or downstream integration imports PyPIExtensionManager and calls install() directly with a package name influenced by untrusted input, an allowlist/blocklist is configured, the PyPI Extension Manager is enabled, and kernels and terminals are disabled or delegated to remote hosts. Fixed in JupyterLab 4.6.2 and 4.5.10.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73626.json
- https://github.com/jupyterlab/jupyterlab/security/advisories/GHSA-whvh-wf3x-g77j
- https://nvd.nist.gov/vuln/detail/CVE-2026-73626
- https://www.vulncheck.com/advisories/jupyterlab-before-authentication-bypass-via-pypiextensionmanager
