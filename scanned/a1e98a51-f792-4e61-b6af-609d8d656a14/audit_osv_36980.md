# [M] Piwigo: Pre-auth SQL injection via date filter parameters in ws_std_image_sql_filter

## Summary
Severity: Medium
Advisory: CVE-2026-27634
Aliases: GHSA-mgqc-3445-qghq
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-27634
Type: osv

## Details
Piwigo is an open source photo gallery application for the web. Prior to version 16.3.0, the four date filter parameters (f_min_date_available, f_max_date_available, f_min_date_created, f_max_date_created) in ws_std_image_sql_filter() are concatenated directly into SQL without any escaping or type validation. This could result in an unauthenticated attacker reading the full database, including user password hashes. This issue has been patched in version 16.3.0.

## References
- https://piwigo.org/release-16.3.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27634.json
- https://github.com/Piwigo/Piwigo/security/advisories/GHSA-mgqc-3445-qghq
- https://nvd.nist.gov/vuln/detail/CVE-2026-27634
- https://github.com/Piwigo/Piwigo/commit/0d5ed1f7778bbe263410446d8cf64594df75bd08
