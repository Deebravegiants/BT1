# [H] Chall-Manager is vulnerable to Path Traversal when extracting/decoding a zip archive

## Summary
Severity: High
Advisory: GHSA-3gv2-v3jx-r9fh
CVE: CVE-2025-53632
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2025-07-10
Source: https://github.com/advisories/GHSA-3gv2-v3jx-r9fh
Type: github-advisory

## Affected
- Go: `github.com/ctfer-io/chall-manager` — affected >=0 <0.1.4

## Details
### Impact
When decoding a scenario (i.e. a zip archive), the path of the file to write is not checked, potentially leading to zip slips.
Exploitation does not require authentication nor authorization, so anyone can exploit it. It should nonetheless not be exploitable as it is **highly** recommended to bury Chall-Manager deep within the infrastructure due to its large capabilities, so no users could reach the system.

### Patches
Patch has been implemented by [commit `47d188f`](https://github.com/ctfer-io/chall-manager/commit/47d188fda5e3f86285e820f12ad9fb6f9930662c) and shipped in [`v0.1.4`](https://github.com/ctfer-io/chall-manager/releases/tag/v0.1.4).

### Workarounds
No workaround exist.

### References
N/A.

## References
- https://github.com/ctfer-io/chall-manager/security/advisories/GHSA-3gv2-v3jx-r9fh
- https://nvd.nist.gov/vuln/detail/CVE-2025-53632
- https://github.com/ctfer-io/chall-manager/commit/47d188fda5e3f86285e820f12ad9fb6f9930662c
- https://github.com/ctfer-io/chall-manager
- https://github.com/ctfer-io/chall-manager/releases/tag/v0.1.4
