# [M] ComposioHQ has a directory traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-3mwv-j45g-vp3w
CVE: CVE-2025-56427
CWE: CWE-200, CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-12-04
Source: https://github.com/advisories/GHSA-3mwv-j45g-vp3w
Type: github-advisory

## Affected
- PyPI: `composio` — affected >=0

## Details
Directory Traversal vulnerability in ComposioHQ v.0.7.20 allows a remote attacker to obtain sensitive information via the _download_file_or_dir function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-56427
- https://github.com/ComposioHQ/composio
- https://github.com/ComposioHQ/composio/blob/master/python/composio/server/api.py#L278
- https://github.com/TOAST-Research/pocs/blob/main/composio/composio_1.md
