# [M] Nextcloud: Limited path traversal via template API if using `{lang}` in config

## Summary
Severity: Medium
Advisory: CVE-2026-45279
Aliases: GHSA-j33j-qph5-4wch
CVSS: 4.4 (CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2026-45279
Type: osv

## Details
Nextcloud is an open source content collaboration platform. In Nextcloud Server from versions 31.0.0 to before 31.0.14, and 32.0.0 to before 32.0.4, if {lang} is used in the template directory config value, non-admin users can in some cases copy arbitrary files (depending on unix permissions) into their own Nextcloud directory via a path traversal. It is recommended that the Nextcloud Server is upgraded to 32.0.4, 31.0.14. It is recommended that the Nextcloud Enterprise Server is upgraded to 32.0.4, 31.0.14, 30.0.17.7, 29.0.17.12, 28.0.14.15

## References
- https://github.com/nextcloud/server/pull/57414/files
- https://hackerone.com/reports/3468140
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45279.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-j33j-qph5-4wch
- https://nvd.nist.gov/vuln/detail/CVE-2026-45279
