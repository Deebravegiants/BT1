# [M] CVE-2024-21539

## Summary
Severity: Medium
Advisory: CVE-2024-21539
Aliases: GHSA-7q7g-4xm8-89cq
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:P)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-21539
Type: osv

## Details
Versions of the package @eslint/plugin-kit before 0.2.3 are vulnerable to Regular Expression Denial of Service (ReDoS) due to improper input sanitization. An attacker can increase the CPU usage and crash the program by exploiting this vulnerability.

## References
- https://security.snyk.io/vuln/SNYK-JS-ESLINTPLUGINKIT-8340627
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/21xxx/CVE-2024-21539.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-21539
- https://github.com/eslint/rewrite/commit/071be842f0bd58de4863cdf2ab86d60f49912abf
