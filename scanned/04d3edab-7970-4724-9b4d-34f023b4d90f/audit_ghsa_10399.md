# [M] kaggle-mcp has a Path Traversal issue

## Summary
Severity: Medium
Advisory: GHSA-q882-jc55-6343
CVE: CVE-2026-7149
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2026-04-27
Source: https://github.com/advisories/GHSA-q882-jc55-6343
Type: github-advisory

## Affected
- PyPI: `kaggle-mcp` — affected >=0

## Details
A vulnerability has been found in dexhunter kaggle-mcp up to 406127ffcb2b91b8c10e20e6c2ca787fbc1dc92d. This vulnerability affects the function prepare_kaggle_dataset of the file src/kaggle_mcp/server.py. The manipulation of the argument competition_id leads to path traversal. The attack is possible to be carried out remotely. The exploit has been disclosed to the public and may be used. This product adopts a rolling release strategy to maintain continuous delivery. Therefore, version details for affected or updated releases cannot be specified. The project was informed of the problem early through an issue report but has not responded yet.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7149
- https://github.com/dexhunter/kaggle-mcp/issues/1
- https://github.com/dexhunter/kaggle-mcp
- https://vuldb.com/submit/802052
- https://vuldb.com/vuln/359748
- https://vuldb.com/vuln/359748/cti
