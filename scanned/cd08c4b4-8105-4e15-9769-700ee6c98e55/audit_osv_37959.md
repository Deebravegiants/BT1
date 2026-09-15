# [H] Coolify: Host RCE via Log Drain secret/env command injection

## Summary
Severity: High
Advisory: CVE-2026-34035
Aliases: GHSA-3xm2-hqg8-4m2p
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-34035
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.466, log drain secret and environment values were interpolated into shell commands without sufficient encoding, allowing an authenticated user to inject commands executed on the host. This issue is fixed in version 4.0.0-beta.466.

## References
- https://github.com/coollabsio/coolify/releases/tag/v4.0.0-beta.466
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34035.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-3xm2-hqg8-4m2p
- https://nvd.nist.gov/vuln/detail/CVE-2026-34035
- https://github.com/coollabsio/coolify/commit/fcd574e1eb1c2f504c48e5be4a5cb6d69f8f1f55
