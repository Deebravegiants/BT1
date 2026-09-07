# [H] JupyterLab: Cross-site scripting (XSS) via crafted settings file (`overrides.json`)

## Summary
Severity: High
Advisory: GHSA-pppj-hq3g-57pj
CVE: CVE-2026-73417
CWE: CWE-116, CWE-79
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:L/SC:N/SI:N/SA:L (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-pppj-hq3g-57pj
Type: github-advisory

## Affected
- PyPI: `jupyterlab` — affected >=4.6.0 <4.6.2
- PyPI: `jupyterlab` — affected >=3.3.0 <4.5.10

## Details
JupyterLab 4.5+ allows notebook settings to be shared and applied through an `overrides.json` file using the `Import` button in the Settings Editor.

Certain notebook display settings were not properly validated before being applied. As a result, a crafted settings file could contain hidden instructions that run as code inside JupyterLab when imported, instead of only changing a display preference.

Because importing a settings file appears harmless, a user could import a file shared by another party without realizing it could do more. On multi-tenant file systems without proper permission control, another user could plant a malicious `overrides.json`.

> CVE assignment pending, GitHub CNA is experiencing severe backlog

### Impact

When a malicious settings file is applied, the embedded code runs with the same access as the affected user. This could allow an attacker to read or modify that user's notebooks and files, and to run code on the user's behalf through the notebook server, including on any connected kernel.

#### User Interaction vs Privileges Required

##### Write access to a loaded settings location

If an attacker can write to a directory JupyterLab loads settings from (e.g. on shared or multi-tenant file system), they could place a crafted `overrides.json` that is applied to another user automatically at startup. This requires high privilages but no action by the victim. 

##### User-imported settings file

A user can import a crafted `overrides.json` through the `Import` button in the Settings Editor, having received it from another party. This requires no privileges but a deliberate action by the victim, who reasonably expects a settings file to change preferences rather than run code.

### Patches

JupyterLab 4.6.2 and 4.5.10 were patched.

### Workarounds

None

### Hardening

1. Treat a settings file as something that can affect how JupyterLab behaves, not only how it appears. Administrators are encouraged to establish a trusted process for distributing configuration rather than relying on ad-hoc importing of shared files.
2. On multi-tenant or shared file systems, restrict write permissions on the application settings directory and other Jupyter configuration paths so that one user cannot place an `overrides.json` (or other configuration) readable by another user. A settings file in these locations is applied automatically, without an import step, so directory permissions are the primary control against cross-user tampering.

## References
- https://github.com/jupyterlab/jupyterlab/security/advisories/GHSA-pppj-hq3g-57pj
- https://github.com/jupyterlab/jupyterlab/pull/19184
- https://github.com/jupyterlab/jupyterlab/pull/19185
- https://github.com/jupyterlab/jupyterlab/pull/19186
- https://github.com/jupyterlab/jupyterlab/commit/be9303f5bcd5308eaeae953c5a3c903046682c2c
- https://github.com/jupyterlab/jupyterlab/commit/f1beab4a2027af4719d6edc07d52d6cf5a39a432
- https://github.com/jupyterlab/jupyterlab
- https://github.com/jupyterlab/jupyterlab/releases/tag/v4.5.10
- https://github.com/jupyterlab/jupyterlab/releases/tag/v4.6.2
