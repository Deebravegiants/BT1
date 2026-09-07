# [M] JupyterLab vulnerable to SXSS in Markdown Preview

## Summary
Severity: Medium
Advisory: GHSA-4m77-cmpx-vjc4
CVE: CVE-2024-22420
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-01-19
Source: https://github.com/advisories/GHSA-4m77-cmpx-vjc4
Type: github-advisory

## Affected
- PyPI: `jupyterlab` — affected >=4.0.0 <4.0.11
- PyPI: `notebook` — affected >=7.0.0 <7.0.7

## Details
### Impact

The vulnerability depends on user interaction by opening a malicious notebook with Markdown cells, or Markdown file using JupyterLab preview feature.

A malicious user can access any data that the attacked user has access to as well as perform arbitrary requests acting as the attacked user.

### Patches

JupyterLab v4.0.11 was patched.

### Workarounds

Users can either disable the table of contents extension by running:

```bash
jupyter labextension disable @jupyterlab/toc-extension:registry
```

### References

Vulnerability reported via the [bug bounty program](https://app.intigriti.com/programs/jupyter/jupyter/detail) [sponsored by the European Commission](https://commission.europa.eu/news/european-commissions-open-source-programme-office-starts-bug-bounties-2022-01-19_en) and hosted on the [Intigriti platform](https://www.intigriti.com/).

## References
- https://github.com/jupyterlab/jupyterlab/security/advisories/GHSA-4m77-cmpx-vjc4
- https://nvd.nist.gov/vuln/detail/CVE-2024-22420
- https://github.com/jupyterlab/jupyterlab/commit/dda0033cd49449572d077bbecd33b18d8d05f48a
- https://github.com/jupyterlab/jupyterlab/commit/e1b3aabab603878e46add445a3114e838411d2df
- https://github.com/jupyterlab/jupyterlab
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/UQJKNRDRFMKGVRIYNNN6CKMNJDNYWO2H
