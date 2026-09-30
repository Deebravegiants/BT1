# [C] Coolify authenticated remote command injection leading to RCE and secret exfiltration

## Summary
Severity: Critical
Advisory: CVE-2026-34038
Aliases: GHSA-qqrq-r9h4-x6wp
CVSS: 9.9 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-06
Source: https://osv.dev/vulnerability/CVE-2026-34038
Type: osv

## Details
Coolify is an open-source and self-hostable tool for managing servers, applications, and databases. Prior to 4.0.0-beta.469, an authenticated remote command injection vulnerability in application deployment handling allows users with application write permissions to achieve remote code execution and exfiltrate sensitive environment variables through deployment logs via fields such as dockerfile_location and deployment commands. This issue is fixed in version 4.0.0-beta.469.

## References
- https://github.com/coollabsio/coolify/releases/tag/v4.0.0-beta.469
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34038.json
- https://github.com/coollabsio/coolify/security/advisories/GHSA-qqrq-r9h4-x6wp
- https://nvd.nist.gov/vuln/detail/CVE-2026-34038
- https://github.com/coollabsio/coolify/commit/23f9156c7306b221101f1ebbe4d3c6b5e2522acd
- https://github.com/coollabsio/coolify/pull/9007
