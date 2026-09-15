# [H] Risk of code injection

## Summary
Severity: High
Advisory: GHSA-pgjj-866w-fc5c
CVE: CVE-2021-21278
CWE: CWE-74
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-pgjj-866w-fc5c
Type: github-advisory

## Affected
- npm: `rsshub` — affected >=0

## Details
### Impact
Some routes use `eval` or `Function constructor`, which may be injected by the target site with unsafe code, causing server-side security issues

### Patches
Temporarily removed the problematic route and added a `no-new-func` rule to eslint
Self-built users should upgrade to 7f1c430 and later as soon as possible

### Credits
Tencent Woodpecker Security Team

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [https://github.com/DIYgod/RSSHub/issues](https://github.com/DIYgod/RSSHub/issues)
* Email us at [i@diygod.me](mailto:i@diygod.me)

## References
- https://github.com/DIYgod/RSSHub/security/advisories/GHSA-pgjj-866w-fc5c
- https://nvd.nist.gov/vuln/detail/CVE-2021-21278
- https://github.com/DIYgod/RSSHub/commit/7f1c43094e8a82e4d8f036ff7d42568fed00699d
- https://github.com/DIYgod/RSSHub
- https://www.npmjs.com/package/rsshub
