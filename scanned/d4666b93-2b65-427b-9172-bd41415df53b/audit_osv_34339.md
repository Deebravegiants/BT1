# [M] Saleor has user enumeration vulnerability due to different error messages

## Summary
Severity: Medium
Advisory: CVE-2025-58442
Aliases: GHSA-8w67-mfm5-fwx5
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2025-09-09
Source: https://osv.dev/vulnerability/CVE-2025-58442
Type: osv

## Details
Saleor is an e-commerce platform. Starting in version 3.21.0 and prior to version 3.21.16, requesting certain fields in the response of `accountRegister` may result in errors that could unintentionally reveal whether a user with the provided email already exists in Saleor. Version 3.21.16 fixes the issue. As a workaround, rate-limit the mutation to reduce the impact.

## References
- https://github.com/saleor/saleor/releases/tag/3.21.16
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/58xxx/CVE-2025-58442.json
- https://github.com/saleor/saleor/security/advisories/GHSA-8w67-mfm5-fwx5
- https://nvd.nist.gov/vuln/detail/CVE-2025-58442
- https://github.com/saleor/saleor/commit/09d671e91ea53a44352d5f685083dc05a2f55e95
- https://github.com/saleor/saleor/commit/b35783838e51cfc118e07d632f64b01bc3a2c4bb
