# [H] DreamFactory has a directory traversal

## Summary
Severity: High
Advisory: GHSA-gv7f-w92j-383q
CVE: CVE-2025-55988
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-03-20
Source: https://github.com/advisories/GHSA-gv7f-w92j-383q
Type: github-advisory

## Affected
- Packagist: `dreamfactory/df-core` — affected >=0 <1.0.4

## Details
An issue in the component /Controllers/RestController.php of DreamFactory Core v1.0.3 allows attackers to execute a directory traversal via an unsanitized URI path.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-55988
- https://github.com/dreamfactorysoftware/df-core/commit/54354605b2ec9afe6ee96756a5a22f6f56828950#diff-e57a7c0af25166ac8f02695307c6c413ca4ba0a48a20b2202ad910654528aab1
- https://github.com/dreamfactorysoftware/df-core
- https://pentest-tools.com/PTT-2025-001-RemoteCodeExecution-via-URL-Path-Traversal.pdf
