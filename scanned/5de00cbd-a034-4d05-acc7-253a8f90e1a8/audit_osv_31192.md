# [M] OpenTofu before 1.8.3 Secret Variable Leaking via Static Evaluation

## Summary
Severity: Medium
Advisory: CVE-2024-58375
Aliases: GHSA-wpr2-j6gr-pjw9, GO-2024-3182
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-16
Source: https://osv.dev/vulnerability/CVE-2024-58375
Type: osv

## Details
OpenTofu versions 1.8.0 through 1.8.2 do not properly restrict sensitive variables and locals when users have opted into static evaluation of module sources, versions, and backend configurations. As a result, values marked as sensitive may be exposed through these configuration elements instead of producing an error. This is fixed in OpenTofu 1.8.3, which adds explicit errors to prevent the use of sensitive values in these contexts.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58375.json
- https://github.com/opentofu/opentofu/security/advisories/GHSA-wpr2-j6gr-pjw9
- https://nvd.nist.gov/vuln/detail/CVE-2024-58375
- https://www.vulncheck.com/advisories/opentofu-before-secret-variable-leaking-via-static-evaluation
