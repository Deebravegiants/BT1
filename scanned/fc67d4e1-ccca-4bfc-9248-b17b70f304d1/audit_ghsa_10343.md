# [M] mkdocs-mcp-plugin has a Path Traversal issue

## Summary
Severity: Medium
Advisory: GHSA-wfr3-hf93-qgg3
CVE: CVE-2026-7159
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-28
Source: https://github.com/advisories/GHSA-wfr3-hf93-qgg3
Type: github-advisory

## Affected
- PyPI: `mkdocs-mcp-plugin` — affected >=0

## Details
A vulnerability was found in douinc mkdocs-mcp-plugin up to 0.4.1. This affects the function read_document/list_documents of the file server.py. Performing a manipulation of the argument docs_dir/file_path results in path traversal. The attack is possible to be carried out remotely. The exploit has been made public and could be used. The vendor confirms, that the "fix will be published within a few days."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7159
- https://github.com/douinc/mkdocs-mcp-plugin/issues/6
- https://github.com/douinc/mkdocs-mcp-plugin/issues/6#issuecomment-4223718119
- https://github.com/douinc/mkdocs-mcp-plugin
- https://vuldb.com/submit/802063
- https://vuldb.com/vuln/359758
- https://vuldb.com/vuln/359758/cti
