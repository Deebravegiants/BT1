# [C] Tabby has a TCC Bypass via Misconfigured Node Fuses

## Summary
Severity: Critical
Advisory: CVE-2025-22136
Aliases: GHSA-prcj-7rvc-26h4
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-01-08
Source: https://osv.dev/vulnerability/CVE-2025-22136
Type: osv

## Details
Tabby (formerly Terminus) is a highly configurable terminal emulator. Prior to 1.0.217 , Tabby enables several high-risk Electron Fuses, including RunAsNode, EnableNodeCliInspectArguments, and EnableNodeOptionsEnvironmentVariable. These fuses create potential code injection vectors even though the application is signed with hardened runtime and lacks dangerous entitlements such as com.apple.security.cs.disable-library-validation and com.apple.security.cs.allow-dyld-environment-variables. This vulnerability is fixed in 1.0.217.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/22xxx/CVE-2025-22136.json
- https://github.com/Eugeny/tabby/security/advisories/GHSA-prcj-7rvc-26h4
- https://nvd.nist.gov/vuln/detail/CVE-2025-22136
- https://github.com/Eugeny/tabby/commit/93513541f7161fa8a59491603cabb6a101c0c08e
