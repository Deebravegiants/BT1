# [M] Kestra task inputFiles accepts traversal filenames for worker file writes

## Summary
Severity: Medium
Advisory: CVE-2026-48129
Aliases: GHSA-q3fw-mvgv-pjr2
CVSS: 6.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:L)
Published: 2026-06-19
Source: https://osv.dev/vulnerability/CVE-2026-48129
Type: osv

## Details
Kestra is an open-source, event-driven orchestration platform. Prior to versions 1.3.19, 1.2.19, 1.1.19, and 1.0.43, Kestra task `inputFiles` writes rendered file names directly under the task working directory. When a flow forwards untrusted execution or webhook data into an `inputFiles` file name, a caller can use `../` path segments to create or overwrite files outside that task working directory on the worker filesystem. Versions 1.3.19, 1.2.19, 1.1.19, and 1.0.43 patch the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/48xxx/CVE-2026-48129.json
- https://github.com/kestra-io/kestra/security/advisories/GHSA-q3fw-mvgv-pjr2
- https://nvd.nist.gov/vuln/detail/CVE-2026-48129
