# [H] Coolify: Command injection via unsanitized persistent storage name in docker volume commands

## Summary
Severity: High
Advisory: CVE-2026-34168
Aliases: GHSA-mh8x-fppq-cp77
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-34168
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.471, the LocalPersistentVolume.name field is interpolated directly into docker volume shell commands without shell argument escaping, allowing an authenticated user to set a storage name containing shell metacharacters and execute commands on managed servers when the resource is deleted. This issue is fixed in version 4.0.0-beta.471.

## References
- https://github.com/coollabsio/coolify/releases/tag/v4.0.0-beta.471
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34168.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-mh8x-fppq-cp77
- https://nvd.nist.gov/vuln/detail/CVE-2026-34168
- https://github.com/coollabsio/coolify/commit/d2064dd4998694cda2eabd00149f7c4d1e94c699
