# [M] Terragrunt: Arbitrary File Deletion via Malicious Module Manifest

## Summary
Severity: Medium
Advisory: GHSA-8394-6f8r-whxg
CVE: CVE-2026-45099
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-08-17
Source: https://github.com/advisories/GHSA-8394-6f8r-whxg
Type: github-advisory

## Affected
- Go: `github.com/gruntwork-io/terragrunt` — affected >=0 <1.0.4

## Details
### Summary

Terragrunt is vulnerable to an arbitrary file deletion flaw when downloading external modules. If a remote module contains a maliciously crafted `.terragrunt-module-manifest` file, Terragrunt can be tricked into deleting files anywhere on the local filesystem that the Terragrunt process has access to.

### Impact

This vulnerability impacts users who download and run untrusted or compromised OpenTofu/Terraform modules. The file deletion occurs during the module download and initialization phase, meaning it happens before OpenTofu or Terraform executes.

In a CI/CD environment or automated runner, an attacker-controlled module could delete arbitrary files, causing denial of service in the deployment pipeline. In a local environment, it could lead to the loss of local source code or configuration files.

This vulnerability is a deletion-only primitive; it does not directly allow for arbitrary code execution (RCE) or data exfiltration.

### Affected Versions

- Terragrunt < `v1.0.4`

### Patches

This vulnerability has been resolved in Terragrunt version `v1.0.4`. 

All users are strongly advised to upgrade.

### Workarounds

If users cannot upgrade immediately, they can mitigate this risk by:

1. Strictly auditing the source URLs of all remote modules used in their Terragrunt configurations.
2. Only consuming modules from trusted, internally vetted sources or verified registries.
3. Pinning module versions to specific, known-safe Git commit SHAs rather than mutable tags or branches.

### Technical Details

Terragrunt tracks files copied into a downloaded module's working directory using a `.terragrunt-module-manifest` file. During the directory cleanup process, Terragrunt decodes the entries in this manifest and removes the listed files to prepare a fresh directory for OpenTofu/Terraform runs.

Previously, Terragrunt trusted the manifest provided by the downloaded module without verifying that the paths scheduled for deletion remained within the boundaries of the module's destination directory. An attacker could forge a manifest containing directory traversal paths, causing the cleanup function to target files outside the cache. The patch introduces a secure boundary check to ensure all cleaned paths remain safely isolated inside the intended manifest folder.

## Credit

Terragrunt would like to thank Francesco Sabiu ([@fsabiu](https://github.com/fsabiu)) for discovering and responsibly disclosing this vulnerability.

## References
- https://github.com/gruntwork-io/terragrunt/security/advisories/GHSA-8394-6f8r-whxg
- https://github.com/gruntwork-io/terragrunt
- https://github.com/gruntwork-io/terragrunt/releases/tag/v1.0.4
