# [M] ZenML is vulnerable to Path Traversal through its `PathMaterializer` class

## Summary
Severity: Medium
Advisory: GHSA-q92x-2x5g-h365
CVE: CVE-2025-8406
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2025-10-05
Source: https://github.com/advisories/GHSA-q92x-2x5g-h365
Type: github-advisory

## Affected
- PyPI: `zenml` — affected >=0.81.0 <0.84.2

## Details
ZenML version 0.83.1 is affected by a path traversal vulnerability in the `PathMaterializer` class. The `load` function uses `is_path_within_directory` to validate files during `data.tar.gz` extraction, which fails to effectively detect symbolic and hard links. This vulnerability can lead to arbitrary file writes, potentially resulting in arbitrary command execution if critical files are overwritten.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-8406
- https://github.com/zenml-io/zenml/commit/5d22a48d7bf6c7f10b748577c2be79cc7969d398
- https://github.com/zenml-io/zenml
- https://huntr.com/bounties/a0880d64-9928-45bf-9663-2cd81582d9e7
