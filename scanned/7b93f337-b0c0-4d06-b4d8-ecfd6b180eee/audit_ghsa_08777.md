# [H] yeoman-environment Vulnerable to Arbitrary Package Installation without User Confirmation

## Summary
Severity: High
Advisory: GHSA-vv9j-gjw2-j8wp
CVE: CVE-2026-42089
CWE: CWE-829
Ecosystem: npm
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-26
Source: https://github.com/advisories/GHSA-vv9j-gjw2-j8wp
Type: github-advisory

## Affected
- npm: `yeoman-environment` — affected >=2.9.0 <6.0.1

## Details
### Impact

`yeoman-environment` versions `>= 2.9.0` and `< 6.0.1` install missing local generator packages from caller-supplied package names without user confirmation. In downstream consumers that pass attacker-controlled project configuration into this path, this can result in arbitrary package installation and code execution during CLI bootstrap.

The vulnerable method is `installLocalGenerators()`, which calls `repository.install()` directly without prompting the user.

### Patches

Upgrade to `yeoman-environment` `6.0.1`, which adds an interactive confirmation prompt before installation ([PR #753](https://github.com/yeoman/environment/pull/753)).

### Workarounds

None.

### Resources

- [Fix commit 78d2af7](https://github.com/yeoman/environment/commit/78d2af7e60294784b8a8b3b3b5099c6874b6a1fa)

## References
- https://github.com/yeoman/environment/security/advisories/GHSA-vv9j-gjw2-j8wp
- https://nvd.nist.gov/vuln/detail/CVE-2026-42089
- https://github.com/yeoman/environment/pull/753
- https://github.com/yeoman/environment/commit/78d2af7e60294784b8a8b3b3b5099c6874b6a1fa
- https://github.com/yeoman/environment
