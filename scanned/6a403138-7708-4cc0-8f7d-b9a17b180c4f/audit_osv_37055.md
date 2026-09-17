# [C] OpenCTI privilege escalation and unauthenticated access via default admin account

## Summary
Severity: Critical
Advisory: CVE-2026-27960
Aliases: GHSA-6vvv-vmfr-xhrx, PYSEC-2026-119
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-05
Source: https://osv.dev/vulnerability/CVE-2026-27960
Type: osv

## Details
OpenCTI is an open source platform for managing cyber threat intelligence knowledge and observables. In versions 6.6.0 through 6.9.12, there is a privilege escalation vulnerability that can be exploited by unauthenticated attackers to query the API as any existing user, including the default admin account. This issue has been fixed in version 6.9.13. As a workaround, the default admin can be disabled using the `APP__ADMIN__EXTERNALLY_MANAGED` configuration.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27960.json
- https://github.com/OpenCTI-Platform/opencti/security/advisories/GHSA-6vvv-vmfr-xhrx
- https://nvd.nist.gov/vuln/detail/CVE-2026-27960
