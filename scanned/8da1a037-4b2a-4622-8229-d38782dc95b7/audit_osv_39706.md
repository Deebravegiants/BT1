# [C] DataEase: Unauthorized Command Execution Vulnerability

## Summary
Severity: Critical
Advisory: CVE-2026-46684
Aliases: GHSA-gp6v-f7mm-458v
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-46684
Type: osv

## Details
DataEase is an open source data visualization and analysis tool. Prior to 2.10.23, DataEase enterprise token handling can let TokenFilter#doFilter() pass X-DE-TOKEN values to TokenUtils.validate(), which checks only token presence and length before userBOByToken(token) uses JWT.decode() without signature verification, allowing forged tokens with chosen uid and oid values to be accepted when licenseValid=true. This issue is fixed in version 2.10.23.

## References
- https://github.com/dataease/dataease/releases/tag/v2.10.23
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46684.json
- https://github.com/dataease/dataease/security/advisories/GHSA-gp6v-f7mm-458v
- https://nvd.nist.gov/vuln/detail/CVE-2026-46684
- https://github.com/dataease/dataease/commit/3efda9d29c0df4300d43bb7874638e03060c3e2d
