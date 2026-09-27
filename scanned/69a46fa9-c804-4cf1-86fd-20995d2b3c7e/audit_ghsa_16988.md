# [C] HashiCorp go-getter Vulnerable to Argument Injection When Fetching Remote Default Git Branches

## Summary
Severity: Critical
Advisory: GHSA-q64h-39hv-4cf7
CVE: CVE-2024-3817
CWE: CWE-88
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-04-17
Source: https://github.com/advisories/GHSA-q64h-39hv-4cf7
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/go-getter` — affected >=1.5.9 <1.7.4

## Details
When go-getter is performing a Git operation, go-getter will try to clone the given repository. If a Git reference is not passed along with the Git url, go-getter will then try to check the remote repository’s HEAD reference of its default branch by passing arguments to the Git binary on the host it is executing on.

An attacker may format a Git URL in order to inject additional Git arguments to the Git call.

Consumers of the go-getter library should evaluate the risk associated with these issues in the context of their go-getter usage and upgrade go-getter to 1.7.4 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-3817
- https://github.com/hashicorp/go-getter/commit/268c11cae8cf0d9374783e06572679796abe9ce9
- https://discuss.hashicorp.com/t/hcsec-2024-09-hashicorp-go-getter-vulnerable-to-argument-injection-when-fetching-remote-default-git-branches/66040
- https://github.com/hashicorp/go-getter
