# [M] Shescape has potential environment variable exposure on Windows with CMD

## Summary
Severity: Medium
Advisory: CVE-2025-30222
Aliases: GHSA-66pp-5p9w-q87j
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:U)
Published: 2025-03-25
Source: https://osv.dev/vulnerability/CVE-2025-30222
Type: osv

## Details
Shescape is a simple shell escape library for JavaScript. Versions 1.7.2 through 2.1.1 are vulnerable to potential environment variable exposure on Windows with CMD. This impact users of Shescape on Windows that explicitly configure `shell: 'cmd.exe'` or `shell: true` using any of `quote`/`quoteAll`/`escape`/`escapeAll`. An attacker may be able to get read-only access to environment variables. This bug has been patched in v2.1.2. For those who are already using v2 of Shescape, no further changes are required. Those who are are using v1 of Shescape should follow the migration guide to upgrade to v2. There is no plan to release a patch compatible with v1 of Shescape. As a workaround, users can remove all instances of `%` from user input before using Shescape.

## References
- https://github.com/ericcornelissen/shescape/releases/tag/v2.1.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/30xxx/CVE-2025-30222.json
- https://github.com/ericcornelissen/shescape/security/advisories/GHSA-66pp-5p9w-q87j
- https://nvd.nist.gov/vuln/detail/CVE-2025-30222
- https://github.com/ericcornelissen/shescape/commit/0a81f1eb077bab8caae283a2490cd7be9af179c6
- https://github.com/ericcornelissen/shescape/pull/1916
