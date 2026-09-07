# [M] JupyterLab PluginManager lock-rule enforcement bypass

## Summary
Severity: Medium
Advisory: GHSA-h5v5-8746-g7mm
CWE: CWE-602, CWE-863
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-h5v5-8746-g7mm
Type: github-advisory

## Affected
- PyPI: `jupyterlab` — affected >=4.6.0 <4.6.2
- PyPI: `jupyterlab` — affected >=4.1.0 <4.5.10

## Details
JupyterLab's plugin manager exposes administrator controls intended to prevent users from enabling or disabling selected plugins. Two server-side enforcement gaps let an authenticated user bypass those controls with direct requests to `/lab/api/plugins`.

### Impact

Users could workaround the plugin manager lock rules via direct API access for either:
- child plugins of extensions covering multiple plugins
- when "lock all" was issued by the administrator

The integrity of data can be impacted, and any hardening or restrictions on permitted user actions (e.g. download/upload limits) within the single-user server can be circumvented if those were implemented with plugins that were locked using the faulty mechanisms.

### Patches

JupyterLab [`v4.6.2`](https://github.com/jupyterlab/jupyterlab/releases/tag/v4.6.2) and [`v4.5.10`](https://github.com/jupyterlab/jupyterlab/releases/tag/v4.5.10) contain the patch.

Users of applications that depend on JupyterLab, such as Notebook v7+, should update `jupyterlab` package too.

### Workarounds

Manually lock all plugins that should be locked. The core plugin identifiers can be found in [the documentation](https://jupyterlab.readthedocs.io/en/latest/extension/extension_points.html#core-plugins) and identifiers for all installed extensions are listed in the [Plugin Manager](https://jupyterlab.readthedocs.io/en/latest/user/extensions.html#managing-plugins-with-plugin-manager).

## References
- https://github.com/jupyterlab/jupyterlab/security/advisories/GHSA-h5v5-8746-g7mm
- https://github.com/jupyterlab/jupyterlab/pull/19184
- https://github.com/jupyterlab/jupyterlab/pull/19185
- https://github.com/jupyterlab/jupyterlab/pull/19186
- https://github.com/jupyterlab/jupyterlab/commit/be9303f5bcd5308eaeae953c5a3c903046682c2c
- https://github.com/jupyterlab/jupyterlab/commit/f1beab4a2027af4719d6edc07d52d6cf5a39a432
- https://github.com/jupyterlab/jupyterlab
- https://github.com/jupyterlab/jupyterlab/releases/tag/v4.5.10
- https://github.com/jupyterlab/jupyterlab/releases/tag/v4.6.2
