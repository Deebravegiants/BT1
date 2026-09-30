# [M] n8n symlink traversal vulnerability in "Read/Write File" node allows access to restricted files

## Summary
Severity: Medium
Advisory: GHSA-ggjm-f3g4-rwmm
CVE: CVE-2025-57749
CWE: CWE-59, CWE-61
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-08-20
Source: https://github.com/advisories/GHSA-ggjm-f3g4-rwmm
Type: github-advisory

## Affected
- npm: `n8n` — affected >=0 <1.106.0

## Details
### Impact
A symlink traversal vulnerability was discovered in the `Read/Write File` node in n8n. While the node attempts to restrict access to sensitive directories and files, it does not properly account for symbolic links (symlinks). An attacker with the ability to create symlinks—such as by using the `Execute Command` node—could exploit this to bypass the intended directory restrictions and read from or write to otherwise inaccessible paths. Users of _n8n.cloud_ are not impacted.

### Patches
Affected users should update to version 1.106.0 or later.

### Workarounds
Until the patch is applied:

- Disable or restrict access to the `Execute Command` node and any other nodes that allow arbitrary file system access.
- Avoid using the `Read/Write File` node on untrusted paths or inputs that could be manipulated via symlinks.

## References
- https://github.com/n8n-io/n8n/security/advisories/GHSA-ggjm-f3g4-rwmm
- https://nvd.nist.gov/vuln/detail/CVE-2025-57749
- https://github.com/n8n-io/n8n/pull/17735
- https://github.com/n8n-io/n8n/commit/c2c3e08cdf33570d9051e659812cbfbdd3c077fd
- https://github.com/n8n-io/n8n
