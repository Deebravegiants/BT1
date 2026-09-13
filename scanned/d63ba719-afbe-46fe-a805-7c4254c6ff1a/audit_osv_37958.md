# [H] Coolify: Host RCE via Sentinel token injection

## Summary
Severity: High
Advisory: CVE-2026-34034
Aliases: GHSA-rpr8-p7jc-x844
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-34034
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.466, the sentinel_token setting is used in shell commands without sufficient validation, allowing an authenticated user with access to server Sentinel settings to inject shell syntax and execute commands on the host when Sentinel is restarted. This issue is fixed in version 4.0.0-beta.466.

## References
- https://github.com/coollabsio/coolify/releases/tag/v4.0.0-beta.466
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34034.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-rpr8-p7jc-x844
- https://nvd.nist.gov/vuln/detail/CVE-2026-34034
- https://github.com/coollabsio/coolify/commit/096d4369e59b3db7ace2db3ca42588c41b9b6019
