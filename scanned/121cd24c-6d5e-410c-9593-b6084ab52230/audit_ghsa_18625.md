# [M] clearml is vulnerable to Path Traversal through its `safe_extract` function

## Summary
Severity: Medium
Advisory: GHSA-579p-qf78-fqm2
CVE: CVE-2025-8917
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-10-05
Source: https://github.com/advisories/GHSA-579p-qf78-fqm2
Type: github-advisory

## Affected
- PyPI: `clearml` — affected >=0 <2.0.2

## Details
A vulnerability in clearml versions before 2.0.2 allows for path traversal due to improper handling of symbolic and hard links in the `safe_extract` function. This flaw can lead to arbitrary file writes outside the intended directory, potentially resulting in remote code execution if critical files are overwritten.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-8917
- https://github.com/clearml/clearml/commit/64fb2bcbdbb87a74af90dd723d5ef4a99fceeb73
- https://github.com/clearml/clearml
- https://huntr.com/bounties/588fcdd1-fea4-4cc2-a9f8-851701dcb576
