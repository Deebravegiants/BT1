# [H] Exposure of sensitive Slack webhook URLs in debug logs and traces

## Summary
Severity: High
Advisory: GHSA-4mjx-2gh5-ph8h
CVE: CVE-2022-39292
CWE: CWE-1258
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-10-10
Source: https://github.com/advisories/GHSA-4mjx-2gh5-ph8h
Type: github-advisory

## Affected
- crates.io: `slack-morphism` — affected >=0 <1.3.2

## Details
### Impact

Debug logs expose sensitive URLs for Slack webhooks that contain private information.

### Patches
The problem is fixed in v1.3.2 which redacts sensitive URLs for webhooks.

### Workarounds
Disabling/filtering debug logs in case you use Slack webhooks using tracing log level and filters.

### References
https://github.com/abdolence/slack-morphism-rust/releases/tag/v1.3.2

### For more information

If you have any questions or comments about this advisory:
* Open an issue in [repo](https://github.com/abdolence/slack-morphism-rust)
* Read our [security policy](https://github.com/abdolence/slack-morphism-rust/blob/master/SECURITY.md)

## References
- https://github.com/abdolence/slack-morphism-rust/security/advisories/GHSA-4mjx-2gh5-ph8h
- https://nvd.nist.gov/vuln/detail/CVE-2022-39292
- https://github.com/abdolence/slack-morphism-rust/commit/48a1da2dc2ad3a5ccc60036d43f6f8fbb2c15f1d
- https://github.com/abdolence/slack-morphism-rust/commit/65ef9fac4f39c4e171e2952a6cf029bb0d059a89
- https://github.com/abdolence/slack-morphism-rust
- https://github.com/abdolence/slack-morphism-rust/releases/tag/v1.3.2
- https://rustsec.org/advisories/RUSTSEC-2022-0087.html
