# [M] Cross-site Scripting in invenio-previewer

## Summary
Severity: Medium
Advisory: GHSA-j9m2-6hq2-4r3c
CVE: CVE-2019-1020019
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2019-07-16
Source: https://github.com/advisories/GHSA-j9m2-6hq2-4r3c
Type: github-advisory

## Affected
- PyPI: `invenio-previewer` — affected >=0 <1.0.0a12

## Details
## Cross-Site Scripting (XSS) vulnerability in JSON, Markdown and iPython Notebook previewers

### Impact
Several Cross-Site Scripting (XSS) vulnerabilities have been found in the JSON, Markdown and iPython Notebook previewers. The vulnerabilities would allow a malicous user to upload a JSON, Markdown or Notebook file with embedded scripts that would be executed by a victims browser.

### Patches
Invenio-Previewer v1.0.0a12 fixes the issue.

### Workarounds
You can remediate the vulnerability without upgrading by disabling the affected previewers. You do this by adding the following to your configuration:

```python
PREVIEWER_PREFERENCE = [
    'csv_dthreejs',
    'simple_image',
    # 'json_prismjs',
    'xml_prismjs',
    # 'mistune',
    'pdfjs',
    # 'ipynb',
    'zip',
]
```

Afterwards, you should not be able to preview JSON, Markdown or iPython Notebook files.

### For more information
If you have any questions or comments about this advisory:
* Email us at [info@inveniosoftware.org](mailto:info@inveniosoftware.org)

## References
- https://github.com/inveniosoftware/invenio-previewer/security/advisories/GHSA-j9m2-6hq2-4r3c
- https://nvd.nist.gov/vuln/detail/CVE-2019-1020019
- https://github.com/advisories/GHSA-j9m2-6hq2-4r3c
- https://github.com/inveniosoftware/invenio-previewer
- https://github.com/pypa/advisory-database/tree/main/vulns/invenio-previewer/PYSEC-2019-26.yaml
