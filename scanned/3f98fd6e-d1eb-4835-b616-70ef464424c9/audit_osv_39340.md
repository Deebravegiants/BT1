# [M] Summarize < 0.15.1 Insecure File Permissions Information Disclosure

## Summary
Severity: Medium
Advisory: CVE-2026-45246
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-05-18
Source: https://osv.dev/vulnerability/CVE-2026-45246
Type: osv

## Details
Summarize prior to 0.15.1 contains an insecure file permission vulnerability in the refresh-free configuration rewrite path that allows local users to read sensitive credentials by exploiting default filesystem permissions. When the refresh-free path rewrites the configuration file, it creates the replacement with default process umask permissions instead of preserving the original file permissions, exposing the config file containing API keys and provider credentials to other local users on shared Unix-like systems.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45246.json
- https://github.com/steipete/summarize/releases/tag/v0.15.2
- https://nvd.nist.gov/vuln/detail/CVE-2026-45246
- https://www.vulncheck.com/advisories/summarize-insecure-file-permissions-information-disclosure
- https://github.com/steipete/summarize/pull/217
- https://github.com/steipete/summarize/commit/9e990193650a23dab73f37d5e1964d574a44098b
- https://github.com/steipete/summarize
