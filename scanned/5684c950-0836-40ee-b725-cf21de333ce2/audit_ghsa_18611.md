# [H] Omni vulnerable to information leak via API

## Summary
Severity: High
Advisory: GHSA-77r9-w39m-9xh5
CVE: CVE-2025-61688
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-10-13
Source: https://github.com/advisories/GHSA-77r9-w39m-9xh5
Type: github-advisory

## Affected
- Go: `github.com/siderolabs/omni` — affected >=1.1.0-beta.0 <1.1.5
- Go: `github.com/siderolabs/omni` — affected >=0 <1.0.2

## Details
### Impact

Omni might leak sensitive information via an API.

### Patches

v1.1.5, v1.0.2 and v1.2.0 contain the patch.

### Workarounds

None.

### References

None.

## References
- https://github.com/siderolabs/omni/security/advisories/GHSA-77r9-w39m-9xh5
- https://nvd.nist.gov/vuln/detail/CVE-2025-61688
- https://github.com/siderolabs/omni
- https://pkg.go.dev/vuln/GO-2025-4022
