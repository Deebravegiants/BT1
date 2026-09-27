# [M] registry-support: decompress can delete files outside scope via relative paths

## Summary
Severity: Medium
Advisory: GHSA-84xv-jfrm-h4gm
CVE: CVE-2024-1485
CWE: CWE-22, CWE-23, CWE-73
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:N/I:H/A:H (CVSS_V3)
Published: 2024-02-14
Source: https://github.com/advisories/GHSA-84xv-jfrm-h4gm
Type: github-advisory

## Affected
- Go: `github.com/devfile/registry-support/registry-library` — affected >=0 <0.0.0-20240206

## Details
A vulnerability was found in the decompression function of registry-support. This issue can be triggered by an unauthenticated remote attacker when tricking a user into opening a specially modified .tar archive, leading to the cleanup process following relative paths to overwrite or delete files outside the intended scope.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-1485
- https://github.com/devfile/registry-support/pull/197
- https://github.com/devfile/registry-support/commit/0e44b9ca6d03fac4fc3f77d37656d56dc5defe0d
- https://access.redhat.com/security/cve/CVE-2024-1485
- https://bugzilla.redhat.com/show_bug.cgi?id=2264106
- https://github.com/advisories/GHSA-84xv-jfrm-h4gm
- https://github.com/devfile/registry-support
