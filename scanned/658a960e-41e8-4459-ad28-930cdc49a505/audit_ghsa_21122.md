# [H] Slack Morphism for Rust before 0.41.0 can leak Slack OAuth client information in application debug logs

## Summary
Severity: High
Advisory: GHSA-99j7-mhfh-w84p
CVE: CVE-2022-31162
CWE: CWE-1258, CWE-200, CWE-212
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-07-20
Source: https://github.com/advisories/GHSA-99j7-mhfh-w84p
Type: github-advisory

## Affected
- crates.io: `slack-morphism` — affected >=0 <0.41.0

## Details
### Impact
Potential/accidental leaking of Slack OAuth client information in application debug logs.

### Patches
More strict and secure debug formatting was introduced in v0.41 for OAuth secret types to avoid the possibility of printing sensitive information in application logs.

### Workarounds
Don't print/output in logs request and responses for OAuth and client configurations.

### For more information
If you have any questions or comments about this advisory:
* Open an issue in the [repo](https://github.com/abdolence/slack-morphism-rust)
* Email us at [me@abdolence.dev](mailto:me@abdolence.dev)

## References
- https://github.com/abdolence/slack-morphism-rust/security/advisories/GHSA-99j7-mhfh-w84p
- https://nvd.nist.gov/vuln/detail/CVE-2022-31162
- https://github.com/abdolence/slack-morphism-rust/pull/133
- https://github.com/abdolence/slack-morphism-rust/commit/4923fb7d458ed28c0302244c54cb4df0acee7ee6
- https://github.com/abdolence/slack-morphism-rust
- https://github.com/abdolence/slack-morphism-rust/releases/tag/v0.41.0
- https://rustsec.org/advisories/RUSTSEC-2022-0086.html
