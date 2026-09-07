# [H] JupyterLab: Image viewer allows XSS when opening malicious image in new browser tab

## Summary
Severity: High
Advisory: GHSA-gx64-gj6p-pc4c
CVE: CVE-2026-73415
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:A/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-gx64-gj6p-pc4c
Type: github-advisory

## Affected
- PyPI: `jupyterlab` — affected >=4.6.0 <4.6.2
- PyPI: `jupyterlab` — affected >=0 <4.5.10

## Details
JupyterLab's image viewer allows for cross-site scripting (XSS) when a specially-crafted image file is opened through the image viewer and then opened in a new tab. This XSS issue can be used to cause remote code execution (RCE) on the JupyterLab server.

### Impact

This vulnerability allows for arbitrary code execution.

### Patches

JupyterLab [`v4.6.2`](https://github.com/jupyterlab/jupyterlab/releases/tag/v4.6.2) and [`v4.5.10`](https://github.com/jupyterlab/jupyterlab/releases/tag/v4.5.10) contain the patch.

### Workarounds

Disable the image viewer plugin:

```
jupyter labextension disable @jupyterlab/imageviewer-extension:plugin
```

Confirm with:

```
jupyter labextension list
```

## References
- https://github.com/jupyterlab/jupyterlab/security/advisories/GHSA-gx64-gj6p-pc4c
- https://github.com/jupyterlab/jupyterlab/pull/19184
- https://github.com/jupyterlab/jupyterlab/pull/19185
- https://github.com/jupyterlab/jupyterlab/pull/19186
- https://github.com/jupyterlab/jupyterlab/commit/be9303f5bcd5308eaeae953c5a3c903046682c2c
- https://github.com/jupyterlab/jupyterlab/commit/f1beab4a2027af4719d6edc07d52d6cf5a39a432
- https://github.com/jupyterlab/jupyterlab
- https://github.com/jupyterlab/jupyterlab/releases/tag/v4.5.10
- https://github.com/jupyterlab/jupyterlab/releases/tag/v4.6.2
