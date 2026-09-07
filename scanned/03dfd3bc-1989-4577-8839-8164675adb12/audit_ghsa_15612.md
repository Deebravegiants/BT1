# [M] HTML injection in JupyterLite leading to DOM Clobbering

## Summary
Severity: Medium
Advisory: GHSA-gj55-2xf9-67rq
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2024-09-06
Source: https://github.com/advisories/GHSA-gj55-2xf9-67rq
Type: github-advisory

## Affected
- PyPI: `jupyterlite-core` — affected >=0 <0.4.1

## Details
### Impact

The vulnerability depends on user interaction by opening a malicious notebook with Markdown cells, or Markdown file using JupyterLab preview feature.

A malicious user can access any data accessible from JupyterLite and perform arbitrary actions in JupyterLite environment.

### Patches

JupyterLite 0.4.1 was patched.

### Workarounds

There is no workaround for the underlying DOM Clobbering susceptibility. However, select plugins can be disabled on deployments which cannot update in a timely fashion to minimise the risk. These are:
- `@jupyterlab/mathjax-extension:plugin` - users will loose ability to preview mathematical equations 
- `@jupyterlab/markdownviewer-extension:plugin` - users will loose ability to open Markdown previews
- `@jupyterlab/mathjax2-extension:plugin` (if installed with optional `jupyterlab-mathjax2` package) - an older version of the mathjax plugin for JupyterLab 4.x

To disable these extensions populate the `disabledExtensions` key in `jupyter-config-data` stanza of `jupyter-lite.json` as documented on https://jupyterlite.readthedocs.io/en/stable/howto/configure/config_files.html#jupyter-lite-json

```json
{
  "jupyter-lite-schema-version": 0,
  "jupyter-config-data": {
    "appName": "My JupyterLite App",
    "disabledExtensions": [
      "@jupyterlab/markdownviewer-extension:plugin",
      "@jupyterlab/mathjax-extension:plugin",
      "@jupyterlab/mathjax2-extension:plugin"
    ]
  }
}
```

To confirm that the plugins were disabled manual inspection of the built page is required.

### References

Upstream advisory: https://github.com/jupyterlab/jupyterlab/security/advisories/GHSA-9q39-rmj3-p4r2

### Notes

This change has a potential to break rendering of some markdown. There is a setting in Sanitizer which allows to revert to the previous sanitizer settings (`allowNamedProperties`).

## References
- https://github.com/jupyterlab/jupyterlab/security/advisories/GHSA-9q39-rmj3-p4r2
- https://github.com/jupyterlite/jupyterlite/security/advisories/GHSA-gj55-2xf9-67rq
- https://github.com/jupyterlite/jupyterlite
