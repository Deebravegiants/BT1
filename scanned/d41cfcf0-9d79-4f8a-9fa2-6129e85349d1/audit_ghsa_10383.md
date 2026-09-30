# [H] Jupyter Notebook Vulnerable to Authentication Token Theft via CommandLinker XSS

## Summary
Severity: High
Advisory: GHSA-rch3-82jr-f9w9
CVE: CVE-2026-40171
CWE: CWE-601, CWE-79
Ecosystem: PyPI, npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-30
Source: https://github.com/advisories/GHSA-rch3-82jr-f9w9
Type: github-advisory

## Affected
- npm: `@jupyter-notebook/help-extension` — affected >=7.0.0 <7.5.6
- PyPI: `notebook` — affected >=7.0.0 <7.5.6
- PyPI: `jupyterlab` — affected >=0 <4.5.7
- npm: `@jupyterlab/help-extension` — affected >=0 <4.5.7

## Details
### Impact

A stored Cross-Site Scripting (XSS) vulnerability in Jupyter Notebook allows attackers to steal authentication tokens from users who open malicious notebook files and interact with elements that the attacker can make look indistinguishable from legitimate controls (single click interaction).

The vulnerability enables complete account takeover through the Jupyter REST API, allowing the attacker to:
1. Read all files
2. Modify/create files
3. Access running kernels and execute arbitrary code
4. Create terminals for shell access

### Patches

Jupyter Notebook 7.5.6 and JupyterLab 4.5.7 include patches for this vulnerability.

### Workarounds

The help extension can be disabled via CLI:

```
jupyter labextension disable @jupyter-notebook/help-extension
jupyter labextension disable @jupyterlab/help-extension
```

### Hardening

The patched versions include a toggle to disable the command linker functionality altogether, for example via `overrides.json`:

```json
{
  "@jupyterlab/apputils-extension:sanitizer": {
    "allowCommandLinker": false
  }
}
```

### Resources

- https://jupyterlab.readthedocs.io/en/latest/user/commands.html#commands-in-markdown-output-and-files

### Acknowledgments

Reported by Daniel Teixeira - NVIDIA AI Red Team

## References
- https://github.com/jupyter/notebook/security/advisories/GHSA-rch3-82jr-f9w9
- https://nvd.nist.gov/vuln/detail/CVE-2026-40171
- https://github.com/jupyter/notebook
- https://jupyterlab.readthedocs.io/en/latest/user/commands.html#commands-in-markdown-output-and-files
