# [M] nextcloud vulnerable to Uncontrolled Resource Consumption

## Summary
Severity: Medium
Advisory: CVE-2023-25816
Aliases: GHSA-53q2-cm29-7j83
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2023-02-24
Source: https://osv.dev/vulnerability/CVE-2023-25816
Type: osv

## Details
Nextcloud is an Open Source private cloud software. Versions 25.0.0 and above, prior to 25.0.3, are subject to Uncontrolled Resource Consumption. A user can configure a very long password, consuming more resources on password validation than desired. This issue is patched in 25.0.3 No workaround is available.

## References
- https://hackerone.com/reports/1820864
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/25xxx/CVE-2023-25816.json
- https://github.com/nextcloud/security-advisories/security/advisories/GHSA-53q2-cm29-7j83
- https://nvd.nist.gov/vuln/detail/CVE-2023-25816
- https://github.com/nextcloud/server/pull/35965
