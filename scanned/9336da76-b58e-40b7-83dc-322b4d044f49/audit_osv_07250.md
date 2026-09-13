# [C] Parse Server GitHub CI workflow vulnerable to RCE through Improper Privilege Management

## Summary
Severity: Critical
Advisory: BIT-parse-2025-67727
Aliases: CVE-2025-67727, GHSA-6w8g-mgvv-3fcj
Ecosystem: Bitnami
Published: 2025-12-18
Source: https://osv.dev/vulnerability/BIT-parse-2025-67727
Type: osv

## Affected
- Bitnami: `parse` — affected >=0 <8.6.0

## Details
Parse Server is an open source backend that can be deployed to any infrastructure that runs Node.js. In versions prior to 8.6.0, a GitHub CI workflow is triggered in a way that grants the GitHub Actions workflow elevated permissions, giving it access to GitHub secrets and write permissions which are defined in the workflow. Code from a fork or lifecycle scripts is potentially included. Only the repository's CI/CD infrastructure is affected, including any public GitHub forks with GitHub Actions enabled. This issue is fixed version 8.6.0 and commits 6b9f896 and e3d27fe.

## References
- https://github.com/parse-community/parse-server/commit/6b9f8963cc3debf59cd9c5dfc5422aff9404ce9d
- https://github.com/parse-community/parse-server/commit/e3d27fea08c8d8bdd9770a689bc2d757cda48b66
- https://github.com/parse-community/parse-server/security/advisories/GHSA-6w8g-mgvv-3fcj
- https://nvd.nist.gov/vuln/detail/CVE-2025-67727
