# [M] Infracost: Terraform Cloud and registry token disclosure via unvalidated hostname

## Summary
Severity: Medium
Advisory: CVE-2026-71494
Aliases: GHSA-6x6c-w9w9-hv4h, GO-2026-6437
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:A/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-71494
Type: osv

## Details
Infracost provides cloud cost intelligence for engineers, AI coding agents, and CI/CD. Prior to 0.10.45, internal/hcl/remote_variables_loader.go and related Terraform Cloud, remote-plan, and Terragrunt registry request paths can attach a configured Terraform Cloud or registry token to a destination hostname derived from untrusted Terraform input without confirming that it is the configured trusted host. When a CI run provides a token while scanning attacker-controlled Terraform, including pull_request_target or a same-repository pull request, an attacker can direct the request to an attacker-controlled host and disclose the token. Standard fork pull_request workflows without secrets are not exposed. This issue is fixed in version 0.10.45.

## References
- https://github.com/infracost/infracost/releases/tag/v0.10.45
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71494.json
- https://github.com/infracost/infracost/security/advisories/GHSA-6x6c-w9w9-hv4h
- https://nvd.nist.gov/vuln/detail/CVE-2026-71494
- https://github.com/infracost/infracost/commit/3d24c757f5e4e60c7259f1b89ad7ceaabcfca86f
- https://github.com/infracost/infracost/pull/3590
