# [M] cakephp/debug_kit: MailPreview contains unsafe reflection

## Summary
Severity: Medium
Advisory: GHSA-p46m-g734-vpc4
CVE: CVE-2026-54614
CWE: CWE-470
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-08-26
Source: https://github.com/advisories/GHSA-p46m-g734-vpc4
Type: github-advisory

## Affected
- Packagist: `cakephp/debug_kit` — affected >=0 <4.10.3
- Packagist: `cakephp/debug_kit` — affected >=5.0.0 <5.2.4

## Details
### Impact

The `MailPreview` feature of debugkit is vulnerable to arbitrary constructor execution. For an application to be vulnerable the following conditions must be true:

1. `debug` mode must be enabled.
2. The hostname must match a 'local' domain or be in an allowlist.

### Patches
5.2.4 and 4.10.3 contain patches for this issue.

### Workarounds
Ensure that debugkit is only part of your development dependencies, and that debug mode is disabled in production environments.

## References
- https://github.com/cakephp/debug_kit/security/advisories/GHSA-p46m-g734-vpc4
- https://github.com/cakephp/debug_kit/pull/1078
- https://github.com/cakephp/debug_kit/commit/7c4d85e984c2334b0f50cd02578a927ff9649e13
- https://github.com/cakephp/debug_kit/commit/c8a2a9e07d56a5e212d95f6947f370f3b5e6eed6
- https://github.com/cakephp/debug_kit
- https://github.com/cakephp/debug_kit/releases/tag/4.10.3
- https://github.com/cakephp/debug_kit/releases/tag/5.2.4
