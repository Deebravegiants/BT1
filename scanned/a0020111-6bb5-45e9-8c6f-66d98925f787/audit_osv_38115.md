# [M] Zammad has incorrect access control in getting_started_controller

## Summary
Severity: Medium
Advisory: CVE-2026-34723
Aliases: GHSA-hcm9-ch62-5727
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-08
Source: https://osv.dev/vulnerability/CVE-2026-34723
Type: osv

## Details
Zammad is a web based open source helpdesk/customer support system. Prior to 7.0.1 and 6.5.4, unauthenticated remote attackers were able to access the getting started endpoint to get access to sensitive internal entity data, even after the system setup was completed. This vulnerability is fixed in 7.0.1 and 6.5.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/34xxx/CVE-2026-34723.json
- https://github.com/zammad/zammad/security/advisories/GHSA-hcm9-ch62-5727
- https://nvd.nist.gov/vuln/detail/CVE-2026-34723
