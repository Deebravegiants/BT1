# [M] OneDev vulnerable to arbitrary file reading for unauthenticated user

## Summary
Severity: Medium
Advisory: CVE-2024-45309
Aliases: GHSA-7wg5-6864-v489
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2024-10-21
Source: https://osv.dev/vulnerability/CVE-2024-45309
Type: osv

## Details
OneDev is a Git server with CI/CD, kanban, and packages. A vulnerability in versions prior to 11.0.9 allows unauthenticated users to read arbitrary files accessible by the OneDev server process. This issue has been fixed in version 11.0.9.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45309.json
- https://github.com/theonedev/onedev/security/advisories/GHSA-7wg5-6864-v489
- https://nvd.nist.gov/vuln/detail/CVE-2024-45309
- https://github.com/theonedev/onedev/commit/4637aaac8c70d41aa789b7fce208b75c6a7b711f
