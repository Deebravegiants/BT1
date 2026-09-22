# [H] Coolify: Authenticated RCE via SHELL_SAFE_COMMAND_PATTERN regression → host root

## Summary
Severity: High
Advisory: CVE-2026-42204
Aliases: GHSA-chg4-63hm-xv9x
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-06
Source: https://osv.dev/vulnerability/CVE-2026-42204
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. From 4.0.0-beta.471 through 4.0.0-beta.473, a regression in SHELL_SAFE_COMMAND_PATTERN allowed ampersands in custom Docker Compose build, start, and pre/post-deployment command fields, allowing an authenticated team member to inject shell commands that execute on the host. This issue is fixed in version 4.0.0-beta.474.

## References
- https://github.com/coollabsio/coolify/releases/tag/v4.0.0-beta.474
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/42xxx/CVE-2026-42204.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-chg4-63hm-xv9x
- https://nvd.nist.gov/vuln/detail/CVE-2026-42204
- https://github.com/coollabsio/coolify/commit/e1aac50b745cf499e710b7e35cd2a9d6a1538dd9
- https://github.com/coollabsio/coolify/pull/9684
