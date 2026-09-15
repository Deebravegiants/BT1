# [C] CVE-2024-21548

## Summary
Severity: Critical
Advisory: CVE-2024-21548
Aliases: GHSA-v9mx-4pqq-h232
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2024-12-18
Source: https://osv.dev/vulnerability/CVE-2024-21548
Type: osv

## Details
Versions of the package bun after 0.0.12 and before 1.1.30 are vulnerable to Prototype Pollution due to improper input sanitization. An attacker can exploit this vulnerability through Bun's APIs that accept objects.**Note:** This issue relates to the widely known and actively developed 'Bun' JavaScript runtime. The bun package on NPM at versions 0.0.12 and below belongs to a different and older project that happened to claim the 'bun' name in the past.

## References
- https://security.snyk.io/vuln/SNYK-JS-BUN-8499549
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/21xxx/CVE-2024-21548.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-21548
- https://github.com/oven-sh/bun/commit/a234e067a5dc7837602df3fb5489e826920cc65a
- https://github.com/oven-sh/bun/pull/14119
