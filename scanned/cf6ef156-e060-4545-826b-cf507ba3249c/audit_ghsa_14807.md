# [H] HashiCorp go-getter Vulnerable to Code Execution On Git Update Via Git Config Manipulation

## Summary
Severity: High
Advisory: GHSA-xfhp-jf8p-mh5w
CVE: CVE-2024-6257
CWE: CWE-77
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2024-06-25
Source: https://github.com/advisories/GHSA-xfhp-jf8p-mh5w
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/go-getter` — affected >=0 <1.7.5

## Details
HashiCorp’s go-getter library can be coerced into executing Git update on an existing maliciously modified Git Configuration, potentially leading to arbitrary code execution. When go-getter is performing a Git operation, go-getter will try to clone the given repository in a specified destination. Cloning initializes a git config to the provided destination and if the repository needs to get updated go-getter will pull the new changes .

An attacker may alter the Git config after the cloning step to set an arbitrary Git configuration to achieve code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6257
- https://github.com/hashicorp/go-getter/commit/268c11cae8cf0d9374783e06572679796abe9ce9
- https://discuss.hashicorp.com/t/hcsec-2024-13-hashicorp-go-getter-vulnerable-to-code-execution-on-git-update-via-git-config-manipulation/68081
- https://github.com/advisories/GHSA-xfhp-jf8p-mh5w
- https://github.com/hashicorp/go-getter
