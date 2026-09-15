# [C] FOSSBilling allows low-privileged staff accounts to perform unauthorized actions via admin API endpoints

## Summary
Severity: Critical
Advisory: CVE-2026-53643
Aliases: GHSA-563q-g4r4-6f9m
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-06
Source: https://osv.dev/vulnerability/CVE-2026-53643
Type: osv

## Details
FOSSBilling is a free, open-source billing and client management system. Versions prior to 0.8.0 allow low-privileged staff accounts to perform unauthorized actions via admin API endpoints. The root cause is a combination of the `can_always_access` module flag (which grants all staff access to certain modules) and insufficient permission checks or unsafe parameter handling on individual endpoints. Version 0.8.0 contains a fix. Some workarounds are available. Restrict staff accounts to only those who need access to sensitive settings and/or use a reverse proxy or WAF to restrict access to the affected endpoints to trusted IP addresses or higher-privilege roles.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53643.json
- https://github.com/FOSSBilling/FOSSBilling/security/advisories/GHSA-563q-g4r4-6f9m
- https://nvd.nist.gov/vuln/detail/CVE-2026-53643
